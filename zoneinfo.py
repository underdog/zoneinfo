#!/usr/bin/python

import os
import sys
import getopt
import shutil
import dns.resolver
import dns.query
import dns.zone
from decimal import *
from dns.exception import DNSException
from dns.rdataclass import *
from dns.rdatatype import *
from operator import itemgetter


def usage():
  print sys.argv[0] + " [OPTIONS]....[FILE | DOMAIN]\n"
  print "[OPTIONS]"
  print "-h, --help\t\t\t\tPrint usage"
  print "-D, --domain=<domain,domain..\t\tDomain(s) to query"
  print "-F, --file=<file>\t\t\tInput file"
  print "-d, --directory=<directory>\t\tOutput directory (default = zonedata)"
  print "-o, --outfile=<file>\t\t\tOutput file for domain successful zone transfers\N"
  print "-n, --nodelete\t\t\t\tDo not delete output directory, if exists (original directory will be moved to <directory>.bak)"
  print "-i, --individual=(true | false)\t\tWrite individual files for each domain (true is default)"
  print "-v, --verbose\t\t\t\tVerbose output"
  sys.exit()

zonedict= {}
zonexfersuccess= {}
pwd = os.getcwd()
outdir = pwd + "/zonedata"
outfile = "axfr.txt"
inputtype = -1
domainlist = []
delete = 1
individual = 1
verbose = 0
domaincount = 0
domainsuccess = 0
domainfailers = 0



try:
  opts, args = getopt.getopt(sys.argv[1:], "hi:nD:F:d:o:v", ["help", "individual=", "nodelete", "domain=", "file=", "directory=", "outfile=", "verbose"])
  if len(sys.argv) == 1:
    usage()
except getopt.GetoptError as err:
  print(err)
  usage()
  sys.exit(2)
for opt, arg in opts:
  if opt in ("-h", "--help"):
    usage()
  elif opt in ("-F", "--file"):
    print "file"
    inputfile = arg
    inputtype = 0
    if not os.path.isfile(inputfile):
      print "Not a valid file"
      sys.exit(0)
    f = open(pwd + "/" + arg, "r")
  elif opt in ("-D", "--domain"):
    domain = arg.split(',')
    inputtype = 1
  elif opt in ("-d", "--directory"):
    if len(arg.split('/')) > 1:
      outdir = arg
    else:
      outdir = pwd + "/" + arg
    pwd = arg
  elif opt in ("-o", "--outfile"):
    outfile = arg
  elif opt in ("-nd", "--nodelete"):
    delete = 0
  elif opt in ("-i", "--individual"):
    if arg in ("on", "On", "ON"):
      individual = 1
      print "individual set to 1"
    elif arg in ("off", "Off", "OFF"):
      individual = 0
      print "individual set to 0"
    else:
      print "Error:  Invalid option for " + opt
      usage()
  elif opt in ("-v", "--verbose"):
      verbose = 1

if inputtype == 0:
  for dom in f.readlines():
    domainlist.append(dom)
elif inputtype == 1:
  for dom in domain:
    domainlist.append(dom)
else:
  print "invalid usage " + sys.argv[1] + " not a valid option"
  usage()
  sys.exit(2)



print '\x1b[H\x1b[2J'

domaincount = len(domain)
outfile = outdir + "/" + outfile
zonesummary = outdir + "/zonelistings.txt"

if not os.path.exists(outdir):
  os.mkdir(outdir)
  os.chdir(outdir)
elif delete == 1:
  shutil.rmtree(outdir)
  os.mkdir(outdir)
  os.chdir(outdir)
else:
  shutil.move(outdir, outdir + ".bak")
  os.mkdir(outdir)
  os.chdir(outdir)

o = open(zonesummary, "w+")
domainlength = 0

for dom in domainlist:
  domain = str.rstrip(dom)
  if len(domain) > domainlength:
    domainlength = len(domain)
  if individual == 1:
    domaininfo = open(outdir + "/" + str.rstrip(domain) + ".txt", "w+")
  print "\n\nGetting NS records for", domain
  try:
    answers = dns.resolver.query(domain, 'NS')
    ns = []
    for rdata in answers:
      n = str(rdata)
      print "Found name server:", n
      ns.append(n)
    for n in ns:
      print "Trying a zone transfer for %s from name server %s" % (domain, n),
      try:
        zone = dns.zone.from_xfr(dns.query.xfr(n, domain, timeout=5, lifetime=10))
        zonedict[n] = str(domain)
	zonexfersuccess[n] = str(domain)
	print "\033[1;32mSUCCESS\033[0m"
      except:
        print "\033[1;31mFAILURE\033[0m"
        pass
  except:
    pass
    #except DNSException, e:
    #  print e.__class__, e

  if (len(zonedict) > 0):
    try:
      domainsuccess= domainsuccess + 1
      for (name, ttl, rdata) in zone.iterate_rdatas('A'):
        if verbose == 1:
	  print domain, "\t", "A\t", name, "\t", ttl, "\t", rdata
        outline = domain +  "\t" +  "A\t" +  str(name) +  "\t" + str(ttl) +  "\t" + str(rdata) + "\n"
        o.write(outline)
	if individual == 1:
          domaininfo.write(outline)
      for (name, ttl, rdata) in zone.iterate_rdatas('MX'):
        if verbose == 1:
          print domain, "\t", "MX\t", name, "\t", ttl, "\t", rdata
        outline = domain +  "\t" +  "MX\t" +  str(name) +  "\t" + str(ttl) +  "\t" + str(rdata) + "\n"
        o.write(outline)
	if individual == 1:
          domaininfo.write(outline)
      for (name, ttl, rdata) in zone.iterate_rdatas('CNAME'):
        if verbose == 1:
          print domain, "\t", "CNAME\t", name, "\t", ttl, "\t", rdata
        outline = domain +  "\t" +  "CNAME\t" +  str(name) +  "\t" + str(ttl) +  "\t" + str(rdata) + "\n"
        o.write(outline)
	if individual == 1:
          domaininfo.write(outline)
      for (name, ttl, rdata) in zone.iterate_rdatas('SRV'):
        if verbose == 1:
          print domain, "\t", "SRV\t", name, "\t", ttl, "\t", rdata
        outline = domain +  "\t" +  "SRV\t" +  str(name) +  "\t" + str(ttl) +  "\t" + str(rdata) + "\n"
        o.write(outline)
	if individual == 1:
          domaininfo.write(outline)
      for (name, ttl, rdata) in zone.iterate_rdatas('TXT'):
        if verbose == 1:
          print domain, "\t", "TXT\t", name, "\t", ttl, "\t", rdata
        outline = domain +  "\t" +  "TXT\t" +  str(name) +  "\t" + str(ttl) +  "\t" + str(rdata) + "\n"
        o.write(outline)
	if individual == 1:
          domaininfo.write(outline)
    except DNSException, e:
      print e.__class__, e
      pass

  zonedict = {}
  zone = ""
  if individual == 1:
    domaininfo.close()

o.close()

o = open(outfile, "w+")
sorted_success = sorted(zonexfersuccess.items(), key=itemgetter(1))

print "\n\nSuccessful zone transfers"
print "Domain\t\t\tName Server"
print "------\t\t\t----------"

#for k, v in zonexfersuccess.iteritems():
for obj in sorted_success:
  line = str(obj[1]) + "\t" + str(obj[0]) + "\n"
  o.write(line)
  if len(str(obj[1])) <= 7:
    print str(obj[1]) + "\t\t\t" + str(obj[0]) + "\t"
  elif len(str(obj[1])) <= 14:
    print str(obj[1]) + "\t\t" + str(obj[0]) + "\t"
  else:
    print str(obj[1]) + "\t" + str(obj[0]) + "\t"
			 
  #for k, v in obj:
    #line = str(v) + "\t" + str(k) + "\n"
    #o.write(line)
    #if (len(str(v)) <= 7):
    #  print str(v) + "\t\t\t" + str(k) + "\t"
    #elif len(str(v)) <= 14:
    #  print str(v) + "\t\t" + str(k) + "\t"
    #else:
    #  print str(v) + "\t" + str(k) + "\t"

o.close()

domainfailure = domaincount - domainsuccess
getcontext().prec = 2
successrate = (Decimal(domainsuccess)/Decimal(domaincount))*100

print "\n\nSummary:"
print "Output Directory:\t\t" + outdir
print "Successful AXFR summary:\t" + outfile
print "Total domains:\t\t\t" + str(domaincount)
print "Total successful axfr:\t\t" + str(domainsuccess)
print "Success rate:\t\t\t" + str(successrate) + "%"
if individual == 0:
  print "Individual domain files:\tDisabled"
else:
  print "Individual domain files:\tEnabled"
