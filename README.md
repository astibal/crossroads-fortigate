# crossroads-fortigate [early development stage]
crossroads callback receiver for FortiGate interface captive portal

## Design
Receive callback from [crossroads](https://github.com/astibal/crossroads) server and push login information to Fortigate. 
Serve radius is needed.

## Howto 
1. Have fortigate configured for external captive portal -> ie. cr0ssr0ads.io:5000/github/login
   + radius server which promiscuously accepts arbitrary usernames and passwords  
     (for testing purposes you can try [raok](https://github.com/astibal/raok), or `pip install raok`)
2. Have github oath2 app configured
3. get [crossroads](https://github.com/astibal/crossroads)
4. set startup script according to `crossroads` start-example.sh
5. install `crossroads-fortigate`, and set up similarly (`crossroads` must have callback set to here)

## How it works
* User browsers will be connecting to `crossroads` site. 
* From there, they will be redirected to github app to get authenticated and also authorized by token, and redirected back to `crossroads`.   
* Once this is done, `crossroads` will connect to `crossroads-fortigate` and receive response what to do   
* `Crossroads`, according to received data,  responds to client browser with pre-filled auto-submit form which responds to Fortigate original authentication request.  
* Browser javascript will submit the form to Fortigate
* Fortigate takes credentials received in the form (username taken from oath site and random generated password) 
and send it to authentication server (this is mandatory). It's typically RADIUS server. 
* This is where it is interesting: you have to accept this arbitrary username/password.  
  For quick testing, grab `raok`, as noted above.
  
  
## Future
- implement radius server taking username/passwords from expiring key/value redis DB:  
  `crossroads-fortigate` writes entries     
  `crossroads-noregrets` radius pops username/pass and accepts request from Fortigate   
  
