Pre-requsite:
  Have Python installed.
  

1) Now ./apporbit-curl.sh

	a) Start to install curl, python if not already installed.
	
	b) Start to download installer binaries
		  Downloading apporbit installer

	c) This will verify system requirements as specified in the requirement documentations
	
		Verifying system informations.
		[====================] 100%   -- [Done]

	
	d) Login to the appOrbit registry using the credentials sent to you by email by your appOrbit sales representative

		Enter the user name: admin
		Password:
		
	e) Enter the build ID by default is latest
		Enter the build id [latest] :
	
	f) Enter the chef server deploy mode :
		1. Deploy on the same host
		2. Do not deploy, will configure it later
		choose the setup type from the above [1] :1
		
	g) New install or upgrade :
		1. New install
		2. Upgrade
		choose the setup type from the above [2] :2
		
	h) Enter the type of SSL certificate type:
		1. Create a new ssl Certificate
		2. Use Existing Certificate
		Choose the type of ssl Certificate [1]:1

	i) Enter the Mode of Deployment
		1. Singe-Tenant
		2. Multi-Tenant
		Choose the type of deployment [1]:1

	j) Enter the user email id for single-tenant deployment [admin@apporbit.com] :
	
	k) Enter hostname or host ip [Default:<IP ADDRESSS>] :
	
	l) Deploying appOrbit management server.
		[====================] 100%   -- [Done]
		
		Please change your default password 'admin1234' by logging into the User Management Console in the UI at https://${hostip}/users

