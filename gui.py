import boto3
import csv
import platform
import re
import sys

from os.path import expanduser
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

class App(QWidget):
    def __init__(self):
        super().__init__()
        self.cbx_list = []
        self.on_activated_list = []
        self.profile_list = ["All",]
        self.title = 'Cresent V1.0.0'
        self.left = 10
        self.top = 10
        self.width = 550
        self.height = 360
        self.get_awscli_profiles()
        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        # Dropdown for AWS Profiles to query
        profile_dropdown_selector = QComboBox(self)
        profile_dropdown_selector.move(24, 15)
        profile_dropdown_selector.activated[str].connect(self.on_activated)
        for profile in self.profile_list:
            profile_dropdown_selector.addItem(profile)

        # Checkboxes for specific EC2 information to query
        public_ip_cbx = QCheckBox("Public IP", self)
        public_ip_cbx.move(25, 45)
        public_ip_cbx.stateChanged.connect(self.get_public_ip)

        instance_id_cbx = QCheckBox("Instance ID", self)
        instance_id_cbx.move(150, 45)
        instance_id_cbx.stateChanged.connect(self.get_instance_id)

        group_id_cbx = QCheckBox("Security Group", self)
        group_id_cbx.move(275, 45)
        group_id_cbx.stateChanged.connect(self.get_group_id)

        instance_state_cbx = QCheckBox("Current State", self)
        instance_state_cbx.move(400, 45)
        instance_state_cbx.stateChanged.connect(self.get_instance_state)

        # Button for advanced EC2 information to query
        advanced_btn = QPushButton("Advanced", self)
        advanced_btn.move(395, 65)

        # Button to execute conditionals on the form
        go_btn = QPushButton("Go", self)
        go_btn.move(395, 95)
        go_btn.clicked.connect(self.go_func)

        # QTextEdit
        output_display = QTextEdit(self)
        output_display.move(10,150)
        output_display.resize(529,200)
        

        self.show()

    # Checkbox trigger responses
    def get_public_ip(self, state):
        if state == Qt.Checked:
            self.cbx_list.append("Public_IP")
            print(self.cbx_list)

    def get_instance_id(self, state):
        if state == Qt.Checked:
            self.cbx_list.append("Instance_ID")
            print(self.cbx_list)

    def get_group_id(self, state):
        if state == Qt.Checked:
            self.cbx_list.append("Group_ID")
            print(self.cbx_list)

    def get_instance_state(self, state):
        if state == Qt.Checked:
            self.cbx_list.append("Instance_State")
            print(self.cbx_list)

    # Get the right path slash for the OS used.
    def slash(self):
        slash = ''
        if platform.system() == 'Windows':
            slash = '\\'
        else:
            slash = '/'
        return slash

    # Returns a List of profiles found in home > .aws > credentials
    def get_awscli_profiles(self):
        home = expanduser("~")
        credentials = home + self.slash() + '.aws' + self.slash() + 'credentials'
        creds_file = open(credentials, 'r').read()
        match = re.findall('(\[.*\])', creds_file)
        aws_profiles = [profile.replace('[', '').replace(']', '')
                        for profile in match
                        ]
        for item in aws_profiles:
            self.profile_list.append(item)

    # Runs get_ec2 for each condition selected in the app
    def go_func(self):
        for item in self.on_activated_list:
            try:
                self.get_ec2(item)
            except:
                # Put link to error window class here
                print("This " +item+ " didn't work.") 

    # Find all EC2 instances in all regions for a single account
    def get_ec2(self, account_profile):
        session = boto3.Session(profile_name=account_profile)
        client = session.client('ec2', region_name='us-east-1')
        ec2_regions = [region['RegionName']
                    for region in client.describe_regions()['Regions']
                    ]
        for region in ec2_regions:
            ec2 = session.resource('ec2', region_name=region)
            instances = ec2.instances.filter()
            with open('EC2_In_All_Accounts.csv', 'ab') as myfile:
                wr = csv.writer(myfile, dialect='excel')
                for instance in instances:
                    try:
                        for tag in instance.tags:
                            if tag['Key'] == 'Name':
                                instancename = tag['Value']
                    except:
                        instancename = 'Has No Name'
                    mylist = [instancename,
                            instance.private_ip_address,
                            instance.state['Name']
                            ]
                    print(mylist)
        self.on_activated_list = []

    # Trigger response for profile_dropdown_selector
    def on_activated(self, text):
        if text == "All":
            self.on_activated_list = self.profile_list[1:]
        else:
            self.on_activated_list.append(text)

# Send stdout and stderr to QTextEdit
# class OutLog:
#     pass

# Class to build error window
# class ErrorWindow():
#     pass

if __name__ == '__main__':
    app = QApplication(sys.argv)
    # sys.stdout = OutLog(edit, sys.stdout)
    # sys.stderr = OutLog(edit, sys.stderr, QtGui.QColor(255,0,0) )
    ex = App()
    sys.exit(app.exec_())
