1) Untar the tar package you recieved from appOrbit sales team
	tar -xvf appOrbitDeploy.tar
	
2) Once you untar the package, you will find the following files.
	Action.py  appOrbitInstall.log  appOrbitLauncher.py  
	apporbit.repo  Config.py  example.local.conf  UserInteract.py  Utility.py
	
3) Now Run appOrbitLauncher.py
	./appOrbitLauncher.py

	a) This will verify system requirements as specified in the requirement documentations
	
		Verifying system informations.
		[====================] 100%   -- [Done]

	
	b) Login to the appOrbit registry using the credentials sent to you by email by your appOrbit sales representative

		Enter the user name: admin
		Password:
		
	c) Enter the build ID by default is latest
		Enter the build id [latest] :
	
	d) Enter the chef server deploy mode :
		1. Deploy on the same host
		2. Do not deploy, will configure it later
		choose the setup type from the above [1] :1
		
	e) New install or upgrade :
		1. New install
		2. Upgrade
		choose the setup type from the above [2] :2
		
	f) Enter the type of SSL certificate type:
		1. Create a new ssl Certificate
		2. Use Existing Certificate
		Choose the type of ssl Certificate [1]:1

	g) Enter the Mode of Deployment
		1. Singe-Tenant
		2. Multi-Tenant
		Choose the type of deployment [1]:1

	h) Enter the user email id for single-tenant deployment [admin@apporbit.com] :
	
	i) Enter hostname or host ip [Default:52.34.220.230] :
	
	j) Deploying appOrbit management server.
		[====================] 100%   -- [Done]
		
		Please change your default password 'admin1234' by logging into the User Management Console in the UI at https://${hostip}/users

