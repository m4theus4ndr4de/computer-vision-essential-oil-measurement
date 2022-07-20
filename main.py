# Computer Vision System Modbus TCP

import cv2
import numpy as np
from pyModbusTCP.server import ModbusServer
from picamera.array import PiRGBArray
from picamera import PiCamera

class ComputerVision_ModbusTCP():

    def __init__(self, ip_ModbusTCP, port_ModbusTCP):

        self.server_ModbusTCP = ModbusServer(host=ip_ModbusTCP, port=port_ModbusTCP, no_block=True)
        self.database_ModbusTCP = self.server_ModbusTCP.data_bank
        self.ip_ModbusTCP = ip_ModbusTCP
        self.port_ModbusTCP = port_ModbusTCP

        self.oil_integer = 0
        self.oil_decimal = 0

    def run(self):

        try:

            def nothing(x):
                pass

            def mouseRGB(event, x, y, flags, param):
                if event == cv2.EVENT_LBUTTONDOWN:
                    colorsB = image[y, x, 0]
                    colorsG = image[y, x, 1]
                    colorsR = image[y, x, 2]
                    colorswitch = image[y, x]
                    cv2.setTrackbarPos('R', 'Trackbars', colorsR)
                    cv2.setTrackbarPos('G', 'Trackbars', colorsG)
                    cv2.setTrackbarPos('B', 'Trackbars', colorsB)
                    print("R:", colorsR, " G:", colorsG, " B:", colorsB, " X:", x, " Y:", y)

            self.server_ModbusTCP.start()
            print("Server Modbus TCP Online at {}".format(self.ip_ModbusTCP))

            cv2.namedWindow('Frame')
            cv2.setMouseCallback('Frame', mouseRGB)

            color = np.zeros((300, 512, 3), np.uint8)

            cv2.namedWindow("Trackbars")

            mode = "0: SCALING 1: TESTING  2: WORKING"
            cv2.createTrackbar(mode, "Trackbars", 0, 2, nothing)

            cv2.createTrackbar("R", "Trackbars", 0, 255, nothing)
            cv2.createTrackbar("G", "Trackbars", 0, 255, nothing)
            cv2.createTrackbar("B", "Trackbars", 0, 255, nothing)

            cv2.createTrackbar('HMin', 'Trackbars', 0, 179, nothing)
            cv2.createTrackbar('SMin', 'Trackbars', 0, 255, nothing)
            cv2.createTrackbar('VMin', 'Trackbars', 0, 255, nothing)
            cv2.createTrackbar('HMax', 'Trackbars', 0, 179, nothing)
            cv2.createTrackbar('SMax', 'Trackbars', 0, 255, nothing)
            cv2.createTrackbar('VMax', 'Trackbars', 0, 255, nothing)

            cv2.setTrackbarPos('R', 'Trackbars', 100)
            cv2.setTrackbarPos('G', 'Trackbars', 20)
            cv2.setTrackbarPos('B', 'Trackbars', 0)
            cv2.setTrackbarPos('HMin', 'Trackbars', 10)
            cv2.setTrackbarPos('SMin', 'Trackbars', 50)
            cv2.setTrackbarPos('VMin', 'Trackbars', 50)
            cv2.setTrackbarPos('HMax', 'Trackbars', 10)
            cv2.setTrackbarPos('SMax', 'Trackbars', 255)
            cv2.setTrackbarPos('VMax', 'Trackbars', 255)

            camera = PiCamera()
            camera.resolution = (640, 480)
            camera.framerate = 30
            camera.brightnesswitch = 45
            camera.contrast = 90

            rawCapture = PiRGBArray(camera, size=(640, 480))

            oil_quantity = 0
            tube_diameter = 29.2
            scale_width = 0
            scale_height = 0

            for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):

                image = frame.array
                hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

                B = cv2.getTrackbarPos("B", "Trackbars")
                G = cv2.getTrackbarPos("G", "Trackbars")
                R = cv2.getTrackbarPos("R", "Trackbars")

                switch = cv2.getTrackbarPos(mode, "Trackbars")
                cv2.imshow("Trackbars", color)
                color[:] = [B, G, R]

                hMin = cv2.getTrackbarPos('HMin', 'Trackbars')
                sMin = cv2.getTrackbarPos('SMin', 'Trackbars')
                vMin = cv2.getTrackbarPos('VMin', 'Trackbars')
                hMax = cv2.getTrackbarPos('HMax', 'Trackbars')
                sMax = cv2.getTrackbarPos('SMax', 'Trackbars')
                vMax = cv2.getTrackbarPos('VMax', 'Trackbars')

                Oil = np.uint8([[[B, G, R]]])
                hsvOil = cv2.cvtColor(Oil, cv2.COLOR_BGR2HSV)
                lowerLimit = np.uint8([hsvOil[0][0][0] - hMin, sMin, vMin])
                upperLimit = np.uint8([hsvOil[0][0][0] + hMax, sMax, vMax])
                mask = cv2.inRange(hsv, lowerLimit, upperLimit)

                result = cv2.bitwise_and(image, image, mask=mask)

                contours, hierarchy = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

                cv2.drawContours(image, contours, -1, (0, 0, 255), 3)

                if len(contours) != 0:

                    if switch == 0:
                        card_contour = max(contours, key=cv2.contourArea)
                        x, y, width, height = cv2.boundingRect(card_contour)
                        cv2.rectangle(image, (x, y), (x + width, y + height), (255, 0, 0), 3)
                        scale_height = 53.98 / height
                        scale_width = 85.6 / width
                        scale_height_card = "{:.2f}".format(scale_height)
                        scale_width_card = "{:.2f}".format(scale_width)
                        height_column = height * scale_height
                        cv2.putText(image, "sh={}, h={}, w={}, sw={}".format(scale_height_card, height, width, scale_width_card), (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)

                    elif switch == 1:
                        oleo_contour = max(contours, key=cv2.contourArea)

                        x, y, width, height = cv2.boundingRect(oleo_contour)
                        cv2.rectangle(image, (x, y), (x + width, y + height), (255, 0, 0), 3)

                        oil_column_height = height * scale_height
                        oil_column_width = width * scale_width
                        oil_column_height_formatted = "{:.2f}".format(oil_column_height)
                        oil_column_width_formatted = "{:.2f}".format(oil_column_width)

                        oil_quantity = 0.0
                        oil_quantity_formatted = "{:.2f}".format(oil_quantity)
                        cv2.putText(image, "oq={}, och={}, ocw={}".format(oil_quantity_formatted, oil_column_height_formatted, oil_column_width_formatted), (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)

                    elif switch == 2:
                        oleo_contour = max(contours, key=cv2.contourArea)

                        x, y, width, height = cv2.boundingRect(oleo_contour)
                        cv2.rectangle(image, (x, y), (x + width, y + height), (255, 0, 0), 3)

                        oil_column = height * scale_height
                        oil_column_width = width * scale_height
                        oil_column_height_formatted = "{:.2f}".format(oil_column)
                        oil_column_width_formatted = "{:.2f}".format(oil_column_width)

                        if oil_column_width >= (tube_diameter - 10):
                            oil_quantity = (oil_column * (np.pi * (tube_diameter ** 2 / 4)) / 1000)

                        else:
                            oil_quantity = 0.0

                        oil_quantity_formatted = "{:.2f}".format(oil_quantity)
                        cv2.putText(image, "oq={}, och={}, ocw={}".format(oil_quantity_formatted, oil_column_height_formatted, oil_column_width_formatted), (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)

                    else:
                        print("switch should be 0, 1 or 2, but it is ", switch, "now")

                else:
                    oil_quantity = 0.0

                cv2.imshow("Frame", image)
                cv2.imshow("Result", result)

                oil_quantity_formatted = "{:.2f}".format(oil_quantity)
                oil_quantity_formatted = float(oil_quantity_formatted)
                self.oil_integer = int(oil_quantity_formatted)
                oil_quantity_decimal = oil_quantity_formatted - self.oil_integer
                oil_quantity_decimal_formatted = oil_quantity_decimal * 100
                self.oil_decimal = int(oil_quantity_decimal_formatted)

                self.database_ModbusTCP.set_input_registers(0, [self.oil_integer])
                self.database_ModbusTCP.set_input_registers(1, [self.oil_decimal])

                print("Integer = {}".format(self.database_ModbusTCP.get_input_registers(0)))
                print("Decimal = {}".format(self.database_ModbusTCP.get_input_registers(1)))

                key = cv2.waitKey(1000)

                rawCapture.truncate(0)

                if key == 27:
                    break

            cv2.destroyAllWindows()

        except Exception as error:

            print("Error: ", error.args)

        except KeyboardInterrupt:

            print("Finished Execution")

        finally:

            self.server_ModbusTCP.stop()
            print("Server Modbus TCP Offline")

computer_vision_modbustcp = ComputerVision_ModbusTCP("127.0.0.1", 502)

computer_vision_modbustcp.run()
