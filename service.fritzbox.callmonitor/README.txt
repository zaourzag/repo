This service addon displays incoming and outgoing calls from the popular german DSL Router called "Fritz!Box",
connecting to port 1012 of the box. This addon also features a number to name and picture resolving against
the internal phonebook of the Fritz!Box. Furthermore, reverse search phone numbers via the API of the company
'klicktel' is implemented. Certain telephone numbers can be excluded from monitoring.

You must enable your Listenport 1012 on the box.
To enable or disable this, enter the following code into your telephone:

#96*5* Callmonitor-Support enabled.
#96*4* Callmonitor-Support disabled.

Some notes

1. If you want to exclude numbers from monitoring enter these numbers (only numbers, no spaces or special chars
   within are allowed) separated by comma and/or space in the provided field. Leave this field blank if you
   don't want to exclude any numbers.

   Example: 08154711, 08154712
   
2. With OS greater then 6.5 the Boxes needs a full qualified login (username/password). I strongly recommended
   that even for older OSs