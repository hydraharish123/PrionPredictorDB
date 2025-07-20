![Aggrescan3D logo](https://bitbucket.org/lcbio/aggrescan3d/wiki/logo.png "Aggrescan3D logo")

This is a repository for Aggrescan3D standalone application developed by the [Laboratory of Computational Biology at University of Warsaw](http://lcbio.pl) in cooperation with the [Laboratory of Protein Folding and Conformational Diseases at Univesity of Barcelona](https://ibb.uab.cat/wp-content/themes/viral/modules/ibb_membres/view_grup.php?CodiGrup=36). 

## Detailed instructions and tutorials are provided on [Aggrescan3D WIKI PAGE](https://bitbucket.org/lcbio/aggrescan3d/wiki/Home) ##

-------------------------------------------
### Table of contents
[1. Introduction](#markdown-header-introduction)

[2. Windows installation guide](#markdown-header-windows-users)

[3. Linux installation guide](#markdown-header-linux-users)  
  
[4. macOS installation guide](#markdown-header-macos-users)

[5. Docker image](#markdown-header-docker-image)

---

## Introduction
*Aggrescan3D* can be installed on Linux, macOS or Windows. This comprehensive tutorial is aimed to guide users through the installation process and is split into three parts for corresponding systems. 

*Aggrescan3D* is a python package using *Python 2.7* version. We *highly* recommend that you use the scientific Anaconda distribution that comes with pre-installed packages 
and conda package manager which allows for an easier and less error prone installation. If you choose to use Anaconda simply go to [their web page](https://www.anaconda.com/download/)
and download a Python 2.7 installation for your target operating system (the installer will suggest installing only for current user for Windows systems we also advise that as managing an all-user install can be more challenging 
and this guide assumes that the user chooses the recommended option). Further steps will give specific instructions for conda users as well as for vanilla python.

##### Tips for users who are not familiar with Python or using command prompt/terminal:
- *Python3.X* is **NOT** the latest version of *Python2.7* and you should always use *Python2.7* to run Aggrescan3D.
- Throughout this tutorial a PATH will be frequently mentioned. PATH is a variable that tells the system where to look for your installed programs when you issue commands. Detailed instructions on how to modify it will be given in appropriate parts of this guide.
- Most sections of this guide contain a correctness test step which can be executed to see wether or not the isntallation was successful. When in doubt run the test. 
- While this tutorial attempts to covers much ground as possible if something goes wrong please contact us for assistance this will also help us improve our software and this guide too!

---

## Windows users

#### 1. Python 2.7 

##### Anaconda distribution 

If you have chosen to use Anaconda this step is already done. 

* Please do note that at this point you should always use  the Anaconda Prompt available in the start menu under that name instead of the regular command prompt.

##### Vanilla Python distribution   

- Follow instructions on [python.org](https://python.org). During the installation process select to include pip and setuptools as those will be necessary. 
- Add Python27/Scripts (by default under C:\Python27\Scripts) folder to your PATH. This folder contains pip which will install Aggrescan3D as well as it is the folder which will contain the Aggrescan3D program once its installed.

Follow the steps described in GFortran section. The folder should be located at ```C:\Python27\Scripts``` by default so either follow the steps in the Control Panel or type:

```
set PATH=%PATH%;C:\Python27\Scripts
``` 

- Note that you have to re-type that in each command prompt in which you want to use *pip* or *Aggrescan3D*.  

##### pip not installed with Python

If you chose not to install pip with your Python installation you need to do that manually. 
Assuming you've already made Python2.7 accessible under command "python", download [this](https://bootstrap.pypa.io/get-pip.py) script, 
change to the directory with downloaded script and run:

```python get-pip.py```
 
##### Correctness test 
To check if pip (hence also Python) are working open a  `command
prompt` (press `cmd + R`; enter "cmd"; hit `enter`) and run the following command:

```pip freeze```

This should list all the packages that you have currently installed.

If you wish to check that you have the correct Python version add the Python binary (python.exe) replacing the example path with your respective one:

```set PATH=%PATH%;C:\Python27``` 

And then type:

```python --version```

Minimum recommended python version for Aggrescan3D is 2.7.12 but as low as 2.7.6 should work. We recommend that you download the latest version from
[python.org](https://python.org).

#### 2. FoldX (optional)

 In order to run stability calculations or mutant calculations FoldX has to be present on the system and PATH to it provided to the program upon running a calculation. 
 
 FoldX is free for academic use and the licence can be obtained at http://foldxsuite.crg.eu/ 

#### 3. *CABS-flex* (optional)

 In order to run the dynamic mode (*highly recommneded*) one has to install *CABS-flex*. Detailed instructions how to do so can be found [here](https://bitbucket.org/lcbio/cabsflex/src/master/README.md)

#### 4. *Aggrescan3D*
##### Anaconda users
In your Anaconda Prompt type:

```conda install -c lcbio aggrescan3d```

##### Vanilla Python
In the regular command prompt type:

```pip install aggrescan3d```

##### Correctness test 
Run a simulation of lcbio's favorite 2gb1 with:

```aggrescan -i 2gb1 -w test_run -v 4```

- If the result is `'aggrescan3d' is not recognized as an internal or external command, operable program or batch file.` it means that your Python's Scripts folder is not on the PATH variable.
- If you see a ```Simulation completed successfully``` message, congratulations you have completed your first *aggrescan3d* simulation. 

To check if the server app works:

```a3d_server```

- Open your favourite web browser (Be warned though - Internet Explorer will not be able to provide full functionality)
- Go to localhost:5000
- ** Some of the app functionality might not work on the Windows system (namely job stopping) and the app is generally less responsive and more prone to hang should work well in most cases though ** 

---

## Linux users ##

#### 1. Python 2.7 

##### Anaconda distribution 

If you have chosen to use Anaconda this step is already done. Anaconda installer should ask you if you want it to be added to your PATH, 
for most users this is desirable because it means that when typing ```python``` it will call Anaconda's Python rather than regular one.  

* Check if the ```python``` command refers to Anaconda Python type:

```python --version```

The output should be something like ```Python 2.7.14 :: Anaconda, Inc. ```. If it is not add a following line to your ~/.bashrc file (found in the user's home directory) 
replacing the path with your anaconda's installation path:

```export $PATH="/absolute/path/to/anaconda2/bin:$PATH"```

and then close and reopen the terminal or simply run:

```source ~/.bashrc```

##### Vanilla Python distribution   

Python 2.7 should be present on all unix systems, to verify the version, open your terminal and type:

```python --version```

We recommended python version for 2.7.12 or higher but earlier releases might also work. 

##### pip not installed with Python

pip should also be installed by default on most unix systems, verify that it works issuing the following command:

```pip freeze```

This should return a list of installed packages for your Python. 
if that is not the case install it using your system's package manager:

```sudo apt-get install python-pip```

#### 2. FoldX (optional)

 In order to run stability calculations or mutant calculations FoldX has to be present on the system and PATH to it provided to the program upon running a calculation. 
 
 FoldX is free for academic use and the licence can be obtained at http://foldxsuite.crg.eu/ 

#### 3. *CABS-flex* (optional)

 In order to run the dynamic mode (*highly recommneded*) one has to install *CABS-flex*. Detailed instructions how to do so can be found [here](https://bitbucket.org/lcbio/cabsflex/src/master/README.md)

#### 4. *Aggrescan3D*
##### Anaconda users
Simply type:

```conda install -c lcbio aggrescan3d```

##### Vanilla Python
Simply type:

```pip install aggrescan3d```

##### **Troubleshooting**

- If pip install fails due to writing rights **do not use sudo pip install.** 

- Depending on your privileges and the way your system is managed you might want or need to install *Aggrescan3D* just for the current user:

```pip install --user aggrescan3d```

- When using the --user flag the binary is placed in a folder that is usually not on your PATH. Usually it is located in your 
```$HOME/.local/bin``` but check if that is the case before continuing. Once you located the binary add its location to your path via editing your .bashrc folder in home directory. Add the line:

```export PATH="$HOME/.local/bin:$PATH"```

##### Correctness test 
Run a simulation of lcbio's favorite 2gb1 with:

```aggrescan -i 2gb1 -w test_run -v 4```

- If the result is `'aggrescan3d' is not recognized as an internal or external command, operable program or batch file.` it means that your Python's Scripts folder is not on the PATH variable.
- If you see a ```Simulation completed successfully``` message, congratulations you have completed your first *aggrescan3d* simulation. 

To check if the server app works:

```a3d_server```

- Open your favourite web browser
- Go to 0.0.0.0:5000 (if the server is not responding depending on the loopback settings localhost:5000 might work)

---

## macOS users

#### 1. Python 2.7 

##### Anaconda distribution 
If you have chosen to use Anaconda this step is already done. Anaconda installer should ask you if you want it to be added to your PATH, 
for most users this is desirable because it means that when typing ```python``` it will call Anaconda's Python rather than regular one.  
* Check if the ```python``` command refers to Anaconda Python type:

```python --version```

If the result doesnt include the word Anaconda it means your system is using other Python version by default this can be changed by prepending Anaconda to your PATH.

- Move into home directory
- Create a .bash_profile file using a text editor (like nano) ```nano .bash_profile```
- Add the line ```export PATH="/absolute/path/to/anaconda2/bin:$PATH"``` with your respective path to anaconda2 installation
- Save the file and relaunch the terminal 

##### Vanilla Python distribution   

macOS comes with *Python2.7* already installed. To check if you have the correct Python version open the `Terminal.app` and type:

```python --version```

If you get the message: `bash: python: command not found` it may mean that your system doesn't have Python installed, or
Python's binary is not in the system `PATH`. To check this run in the `Terminal.app` the following command:

```/Library/Frameworks/Python.framework/Versions/2.7/bin/python --version```

If you still get the message: `bash: python: command not found` you need to install *Python2.7*. Otherwise add Python's
binary to the system's `PATH` by running in the `Terminal.app` the following command and then reopen the terminal:

```echo "export PATH=/Library/Frameworks/Python.framework/Versions/2.7/bin/:$PATH" >> ~/.bash_profile```

##### pip not installed with Python

Assuming you've already installed Python2.7 and made it accessible under command "python" simply install pip via setuptools by:

```sudo easy_install pip```

#### 2. FoldX (optional)

 In order to run stability calculations or mutant calculations FoldX has to be present on the system and PATH to it provided to the program upon running a calculation. 
 
 FoldX is free for academic use and the licence can be obtained at http://foldxsuite.crg.eu/ 

#### 3. *CABS-flex* (optional)

 In order to run the dynamic mode (*highly recommneded*) one has to install *CABS-flex*. Detailed instructions how to do so can be found [here](https://bitbucket.org/lcbio/cabsflex/src/master/README.md)

#### 4. *Aggrescan3D*
##### Anaconda users
Simply type:

```conda install -c lcbio aggrescan3d```

##### Vanilla Python
Simply type:

```pip install aggrescan3d```

*For macOS "El Captian" are newer `six` library comes preinstalled and may cause installation erros. Try running: `pip install aggrescan3d --ignore-installed six` instead.*

##### Correctness test 
Run a simulation of lcbio's favorite 2gb1 with:

```aggrescan -i 2gb1 -w test_run -v 4```

- If the result is `'aggrescan3d' is not recognized as an internal or external command, operable program or batch file.` it means that your Python's Scripts folder is not on the PATH variable.
- If you see a ```Simulation completed successfully``` message, congratulations you have completed your first *aggrescan3d* simulation. 

To check if the server app works:

```a3d_server```

- Open your favourite web browser
- Go to 0.0.0.0:5000 (if the server is not responding depending on the loopback settings localhost:5000 might work)

---

## Docker image

*Aggrescan3D* is also available as a docker image and this tutorial will guide the user through how to create a local, always available *Aggrescan3D* server on their PC using the Docker technology. This could also be a good workaround for
users facing compatibility and installation issues.
 
*Please note we cannot include FoldX nor Modeller software in distributed images as they require a licence to run. We however explain how to get those running easly and unlok the full potentail of Aggrescan3D inside a Docker container*
 
- ```lcbio/a3d_server``` - [conda](https://hub.docker.com/r/lcbio/a3d_server/) based distribution. Included Dockerfile should allow the users to build a Docker Image with dynamic mode support

 
### Beginner's tutorial
 
 While we cannot provide a ground-up guide on Docker usage we do provide basic instructions and further reading material that should make it possible to use this without prior experience. This tutorial is Linux oriented but Docker is also available on Windows10 Pro.
 
#### 1. Installing Docker
 
 Please refer to the [docs](https://docs.docker.com/install/) which contain detailed and well written guides for different systems:
 
 We also recommend you read [this](https://docs.docker.com/get-started/) starter article on the docker docs
 
 And [this](https://docs.docker.com/install/linux/linux-postinstall/) post-installation tips (especially if you get permission errors and have to always run docker with sudo)
 
#### 2. Using dynamic mode in the container
 
 To do that one has to create their own image based on our conda image.
 
 - Create a new folder and cd into it ```mkdir docker_build && cd docker_build```
 - Create a Dockerfile and copy the contents which can be found [here](https://hub.docker.com/r/lcbio/a3d_server/)
 - Uncomment the suggested lines and replace XXXX with your Modeller licence key
 - Run ```docker build -t image_name .``` 
 - If the process is successful the image will be available under 'image_name'
 
#### 3. Get the *Aggrescan3D* image (skip if you did point 2)
  
 To make the image available on your system run:
```
#!bash
docker pull lcbio/a3d_server
```
#### 4. Running the Docker container
 
 The basic goal of the conatiner is to provide a server-like service locally. We recommend to use a following command (explained below):
 
```
#!bash
docker run --name a3d_service -p 5000:5000 -v /your/absolute/path/to/FoldX:/home/FoldX --restart unless-stopped -d a3d_server
```
 - The name command will assign a name to your container which will make it easier to manipulate it in the future
 - The -p option exposes your container's 5000 port to your machine's 5000 port. This will mean that you can access the service from your machine. 
 - The -v option mounts your FoldX folder inside the container which makes it available to the service. This is necessary if you wish to use the stability calculations or mutations. Please leave the second part (after ':') unchanged and make sure you provide an absoulte path.
 - The restrart unless-stopped will restart the container on system restart meaning it will be always available (Blocking port 5000 though). 
 - The -d options means detach - the container will run in the background  
 
 Addition interaction with the container can be performed as follows:

 - To stop the service: ```docker stop a3d_service```
 - To start it again: ```docker start a3d_service```
 - To restart a running container (in case it hung, etc): ```docker start a3d_service ```
 - To copy files from container to local system (results on the container are stored inside /opt/conda/lib/python2.7/site-packages/a3d_gui/computations/): ```docker cp a3d_service:path/inside/the/container local/path```
 - To delete the container (*this will delete all the simulation results that were not copied to the filesystem!*): ```docker rm a3d_service```

 To interact with the container's console for purposes other than the server run it via which will give access to a shell with aggrescan installed: 
 
```docker run --name my_container a3d_server /bin/bash```
 
#### 5. Further reading 
 
 - Running docker images [explained](https://www.pluralsight.com/guides/docker-a-beginner-guide)
 - We found [this](https://docker-curriculum.com/) guide to be quite informative and well-written. 




