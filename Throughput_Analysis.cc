/* -*- Mode:C++; c-file-style:"gnu"; indent-tabs-mode:nil; -*- */
/*
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License version 2 as
 * published by the Free Software Foundation;
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program; if not, write to the Free Software
 * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
 */

////////////////////////////EE 289 Project 1 Template///////////////////

#include "ns3/core-module.h"
#include "ns3/point-to-point-module.h"
#include "ns3/network-module.h"
#include "ns3/applications-module.h"
#include "ns3/wifi-module.h"
#include "ns3/mobility-module.h"
#include "ns3/csma-module.h"
#include "ns3/internet-module.h"
#include "ns3/flow-monitor-module.h"
#include "ns3/constant-position-mobility-model.h"
#include "ns3/propagation-loss-model.h"

using namespace ns3;

NS_LOG_COMPONENT_DEFINE ("ProjectOneTemplate");

int main (int argc, char *argv[])
{
  uint32_t packetSize = 1000;
  uint32_t n=2;
  double dist = 100;


  CommandLine cmd;
  cmd.AddValue ("packetSize", "size of application packet sent", packetSize);
  cmd.AddValue ("n", "number of nodes", n);
  cmd.AddValue ("dist", "distance between nodes", dist);

  cmd.Parse (argc, argv);


/////Create Nodes

  NodeContainer nodes;
  nodes.Create (n);


/////Preapare WiFi Channel
  WifiHelper wifi;

  wifi.SetStandard (WIFI_PHY_STANDARD_80211b);

  YansWifiPhyHelper wifiPhy =  YansWifiPhyHelper::Default ();
  wifiPhy.Set ("EnergyDetectionThreshold", DoubleValue (-80) );
  wifiPhy.Set ("CcaMode1Threshold", DoubleValue(-81));               //receiving packets at -80 in the distance of 360, but not at 370


  YansWifiChannelHelper wifiChannel;
  wifiChannel.SetPropagationDelay ("ns3::ConstantSpeedPropagationDelayModel");
  wifiChannel.AddPropagationLoss ("ns3::FriisPropagationLossModel");


  wifiPhy.SetChannel (wifiChannel.Create ());

  wifi.SetRemoteStationManager ("ns3::ConstantRateWifiManager",
                                "DataMode",StringValue ("DsssRate2Mbps"),
                                "ControlMode",StringValue ("DsssRate1Mbps"));

/////Fragmentation and RTS/CTS properties
  Config::SetDefault ("ns3::WifiRemoteStationManager::FragmentationThreshold", StringValue ("2200"));
  Config::SetDefault ("ns3::WifiRemoteStationManager::RtsCtsThreshold", StringValue ("2200"));


/////Set it to adhoc mode
  WifiMacHelper wifiMac;


/////Add the sensing of traffic
  wifiMac.SetType ("ns3::AdhocWifiMac");
  NetDeviceContainer devices = wifi.Install (wifiPhy, wifiMac, nodes);
  MobilityHelper mobility;

////////////////////////Grid Location Model/////////////////////////////////
  mobility.SetPositionAllocator ("ns3::GridPositionAllocator",
                                "MinX", DoubleValue (0.0),
                                "MinY", DoubleValue (0.0),
                                "DeltaX", DoubleValue (dist),
                                "DeltaY", DoubleValue (20.0),
                                "GridWidth", UintegerValue (n),
                                "LayoutType", StringValue ("RowFirst"));



////////////////////////Random Rectangle Location Model/////////////////////////////////
  /*mobility.SetPositionAllocator ("ns3::RandomRectanglePositionAllocator",
                                "X", StringValue ("ns3::UniformRandomVariable[Min=0|Max=500]"),
                                "Y", StringValue ("ns3::UniformRandomVariable[Min=0|Max=500]"));

  */

////////////////////////Random Disc Location Model/////////////////////////////////
/* mobility.SetPositionAllocator ("ns3::RandomDiscPositionAllocator",
                                "X", StringValue ("500"),
                                "Y", StringValue ("500"),
                                "Rho", StringValue ("ns3::UniformRandomVariable[Min=350|Max=350]"),
                                "Theta", StringValue ("ns3::UniformRandomVariable[Min=0|Max=6.283]"));

*/

  mobility.SetMobilityModel ("ns3::ConstantPositionMobilityModel");

  mobility.Install (nodes);

////////////////////Adding mobility model to the receiver and putting it in the center in the disc model//////
/*  MobilityHelper mobility_Rx;
  Ptr<ListPositionAllocator> positionAlloc = CreateObject<ListPositionAllocator> ();
  positionAlloc->Add (Vector (500.0, 500.0, 0.0));
  mobility_Rx.SetPositionAllocator (positionAlloc);
  mobility_Rx.SetMobilityModel ("ns3::ConstantPositionMobilityModel");
  mobility_Rx.Install (nodes.Get (n/2));
*/


/////Adding IP Stack

  InternetStackHelper internet;
  internet.Install (nodes);
  Ipv4AddressHelper address;
  address.SetBase ("10.1.1.0", "255.255.255.0");
  Ipv4InterfaceContainer i;
  i = address.Assign (devices);



/////Adding Applications
  UdpServerHelper myServer (45);
  ApplicationContainer serverApp = myServer.Install (nodes.Get (n/2));
  serverApp.Start(Seconds(0.0));
  serverApp.Stop(Seconds(20.0));


  OnOffHelper myClient ("ns3::UdpSocketFactory", InetSocketAddress (i.GetAddress (n/2), 45));
  myClient.SetAttribute ("PacketSize", UintegerValue (packetSize));
  myClient.SetAttribute ("OnTime",  StringValue ("ns3::ConstantRandomVariable[Constant=1]"));
  myClient.SetAttribute ("OffTime", StringValue ("ns3::ConstantRandomVariable[Constant=0]"));
  myClient.SetAttribute ("DataRate", StringValue ("3000000bps"));

  ApplicationContainer clientApps;

 for(uint32_t j=0;j<n; j++)
  {

        if (j!=n/2){
        myClient.SetAttribute ("StartTime", TimeValue (Seconds (5.0 + .001*j)));
        clientApps.Add (myClient.Install (nodes.Get (j)));
        }
  }

/////Adding initial application to avoid problems with ARP collisions
  uint16_t  echoPort = 9;
  UdpEchoClientHelper echoClientHelper (i.GetAddress (n/2), echoPort);
  echoClientHelper.SetAttribute ("MaxPackets", UintegerValue (1));
  echoClientHelper.SetAttribute ("Interval", TimeValue (Seconds (0.1)));
  echoClientHelper.SetAttribute ("PacketSize", UintegerValue (10));
  ApplicationContainer pingApps;

  for(uint32_t j=0;j<n; j++)
  {
        if (j!=n/2){
        echoClientHelper.SetAttribute ("StartTime", TimeValue (Seconds (0.001+.005*j)));
        pingApps.Add (echoClientHelper.Install (nodes.Get (j)));
        }
  }


///// Tracing
  wifiPhy.EnablePcap ("project1a", n/2, 0);


/////Setup Simulator  
  Simulator::Stop (Seconds (20.0));

  Simulator::Run ();
  Simulator::Destroy ();

/////Count number of packets received
  uint32_t totalPacketsThrough = DynamicCast<UdpServer> (serverApp.Get (0))->GetReceived ();

  std::cout << "Total Packets Received: " << totalPacketsThrough << '\n';

  return 0;
}
