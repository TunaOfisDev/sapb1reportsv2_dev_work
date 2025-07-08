How to Install Postman on Ubuntu 22.04
By Karim Buzdar. Published on 07/07/2023.
Postman is a powerful collaboration platform and an essential tool for API development and testing. It provides developers with a good user experience and a friendly interface to design, document, and execute API requests effortlessly. With its intuitive interface and extensive set of features, Postman simplifies the process of building, testing, and documenting APIs.

Postman supports various HTTP methods, authentication types, and request parameters, allowing developers to interact with APIs efficiently. Postman also offers advanced features like automated testing, mocking, and monitoring, which aid in streamlining the API development workflow.

In this guide, we will demonstrate how to install Postman API development and testing tool on Ubuntu 22.04 Jammy Jellyfish distribution.

Installing Postman on Ubuntu 22.04
Installing Postman on Ubuntu 22.04 is a straightforward process. Follow the steps below to install Postman on your system:

1. Update System Packages
Open a terminal by pressing ‘Ctrl+Alt+T’ and execute below-given to update the package lists for upgrades and new installations:


$ sudo apt update


2. Install Snapd on Ubuntu 22.04
Postman can be installed using the Snap package manager. If you don’t have Snapd installed, you can install it by running below-given:


$ sudo apt install snapd


3. Installing Postman on Ubuntu 22.04 using snap
Once Snapd is installed, you can start the Postman installation. Use below-given to install Postman:

$ sudo snap install postman



4. Launch Postman using Command line
After the installation is complete, you can launch Postman by running the below-given in the terminal:

$ postman
Postman will open, and you can start using it to make API requests and test your APIs.

5. Create Desktop icon for using Postman
You can also create a desktop icon for your ease. To create Postman desktop icon on Ubuntu, create a file with name ‘postman.desktop’ and now open it using this command:


$ sudo nano /usr/share/applications/Postman.desktop
Now, paste the below lines in the ‘Postman.desktop’ config file.

[Desktop Entry]
Name=Postman API Tool
GenericName=Postman
Comment=Testing API
Exec=/usr/bin/Postman/Postman
Terminal=false
X-MultipleArgs=false
Type=Application
Icon=/usr/bin/Postman/app/resources/app/assets/icon.png
StartupWMClass=Postman
StartupNotify=true




You can change icon path and other conditions based on your requirements. Press ‘Ctrl+s’ and exit from this file using ‘Ctrl+x’.

Launch the postman using the GUI. Click on ‘Activities’ and type ‘postman’ in the application search bar:




You will see the postman icon in the search result. Click on it and launch the postman interface for testing your API.

That’s it! You have successfully installed Postman on Ubuntu 22.04. Enjoy using it for API development and testing.



Conclusion
In this tutorial, we learned how we can install Postman on Ubuntu 22.04 using the command line and how to create a Postman desktop icon using the command line. Its comprehensive set of tools and integrations make it a go-to choice for developers, enabling them to streamline their API development process and accelerate their productivity. To learn more about postman, you can create an account and use it.