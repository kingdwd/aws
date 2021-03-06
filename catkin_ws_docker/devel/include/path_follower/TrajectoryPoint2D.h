// Generated by gencpp from file path_follower/TrajectoryPoint2D.msg
// DO NOT EDIT!


#ifndef PATH_FOLLOWER_MESSAGE_TRAJECTORYPOINT2D_H
#define PATH_FOLLOWER_MESSAGE_TRAJECTORYPOINT2D_H


#include <string>
#include <vector>
#include <map>

#include <ros/types.h>
#include <ros/serialization.h>
#include <ros/builtin_message_traits.h>
#include <ros/message_operations.h>


namespace path_follower
{
template <class ContainerAllocator>
struct TrajectoryPoint2D_
{
  typedef TrajectoryPoint2D_<ContainerAllocator> Type;

  TrajectoryPoint2D_()
    : t(0.0)
    , x(0.0)
    , y(0.0)
    , theta(0.0)
    , kappa(0.0)
    , kappa_dot(0.0)
    , v(0.0)
    , a(0.0)
    , jerk(0.0)
    , delta_theta(0.0)
    , d(0.0)
    , a_lat(0.0)  {
    }
  TrajectoryPoint2D_(const ContainerAllocator& _alloc)
    : t(0.0)
    , x(0.0)
    , y(0.0)
    , theta(0.0)
    , kappa(0.0)
    , kappa_dot(0.0)
    , v(0.0)
    , a(0.0)
    , jerk(0.0)
    , delta_theta(0.0)
    , d(0.0)
    , a_lat(0.0)  {
  (void)_alloc;
    }



   typedef double _t_type;
  _t_type t;

   typedef double _x_type;
  _x_type x;

   typedef double _y_type;
  _y_type y;

   typedef double _theta_type;
  _theta_type theta;

   typedef double _kappa_type;
  _kappa_type kappa;

   typedef double _kappa_dot_type;
  _kappa_dot_type kappa_dot;

   typedef double _v_type;
  _v_type v;

   typedef double _a_type;
  _a_type a;

   typedef double _jerk_type;
  _jerk_type jerk;

   typedef double _delta_theta_type;
  _delta_theta_type delta_theta;

   typedef double _d_type;
  _d_type d;

   typedef double _a_lat_type;
  _a_lat_type a_lat;





  typedef boost::shared_ptr< ::path_follower::TrajectoryPoint2D_<ContainerAllocator> > Ptr;
  typedef boost::shared_ptr< ::path_follower::TrajectoryPoint2D_<ContainerAllocator> const> ConstPtr;

}; // struct TrajectoryPoint2D_

typedef ::path_follower::TrajectoryPoint2D_<std::allocator<void> > TrajectoryPoint2D;

typedef boost::shared_ptr< ::path_follower::TrajectoryPoint2D > TrajectoryPoint2DPtr;
typedef boost::shared_ptr< ::path_follower::TrajectoryPoint2D const> TrajectoryPoint2DConstPtr;

// constants requiring out of line definition



template<typename ContainerAllocator>
std::ostream& operator<<(std::ostream& s, const ::path_follower::TrajectoryPoint2D_<ContainerAllocator> & v)
{
ros::message_operations::Printer< ::path_follower::TrajectoryPoint2D_<ContainerAllocator> >::stream(s, "", v);
return s;
}

} // namespace path_follower

namespace ros
{
namespace message_traits
{



// BOOLTRAITS {'IsFixedSize': True, 'IsMessage': True, 'HasHeader': False}
// {'std_msgs': ['/opt/ros/kinetic/share/std_msgs/cmake/../msg'], 'geometry_msgs': ['/opt/ros/kinetic/share/geometry_msgs/cmake/../msg'], 'sensor_msgs': ['/opt/ros/kinetic/share/sensor_msgs/cmake/../msg'], 'path_follower': ['/data/yang/code/aws/catkin_ws_docker/src/path_follower/msg']}

// !!!!!!!!!!! ['__class__', '__delattr__', '__dict__', '__doc__', '__eq__', '__format__', '__getattribute__', '__hash__', '__init__', '__module__', '__ne__', '__new__', '__reduce__', '__reduce_ex__', '__repr__', '__setattr__', '__sizeof__', '__str__', '__subclasshook__', '__weakref__', '_parsed_fields', 'constants', 'fields', 'full_name', 'has_header', 'header_present', 'names', 'package', 'parsed_fields', 'short_name', 'text', 'types']




template <class ContainerAllocator>
struct IsFixedSize< ::path_follower::TrajectoryPoint2D_<ContainerAllocator> >
  : TrueType
  { };

template <class ContainerAllocator>
struct IsFixedSize< ::path_follower::TrajectoryPoint2D_<ContainerAllocator> const>
  : TrueType
  { };

template <class ContainerAllocator>
struct IsMessage< ::path_follower::TrajectoryPoint2D_<ContainerAllocator> >
  : TrueType
  { };

template <class ContainerAllocator>
struct IsMessage< ::path_follower::TrajectoryPoint2D_<ContainerAllocator> const>
  : TrueType
  { };

template <class ContainerAllocator>
struct HasHeader< ::path_follower::TrajectoryPoint2D_<ContainerAllocator> >
  : FalseType
  { };

template <class ContainerAllocator>
struct HasHeader< ::path_follower::TrajectoryPoint2D_<ContainerAllocator> const>
  : FalseType
  { };


template<class ContainerAllocator>
struct MD5Sum< ::path_follower::TrajectoryPoint2D_<ContainerAllocator> >
{
  static const char* value()
  {
    return "63ab900fed4c2c35d54c1d98c787e72b";
  }

  static const char* value(const ::path_follower::TrajectoryPoint2D_<ContainerAllocator>&) { return value(); }
  static const uint64_t static_value1 = 0x63ab900fed4c2c35ULL;
  static const uint64_t static_value2 = 0xd54c1d98c787e72bULL;
};

template<class ContainerAllocator>
struct DataType< ::path_follower::TrajectoryPoint2D_<ContainerAllocator> >
{
  static const char* value()
  {
    return "path_follower/TrajectoryPoint2D";
  }

  static const char* value(const ::path_follower::TrajectoryPoint2D_<ContainerAllocator>&) { return value(); }
};

template<class ContainerAllocator>
struct Definition< ::path_follower::TrajectoryPoint2D_<ContainerAllocator> >
{
  static const char* value()
  {
    return "#Header header  not sent directly\n\
float64 t\n\
float64 x\n\
float64 y\n\
float64 theta\n\
float64 kappa\n\
float64 kappa_dot\n\
float64 v\n\
float64 a\n\
float64 jerk\n\
float64 delta_theta     # heading misalignment with center line\n\
float64 d               # offset to center line\n\
float64 a_lat           # lateral (to traj not to center line!) acceleration\n\
";
  }

  static const char* value(const ::path_follower::TrajectoryPoint2D_<ContainerAllocator>&) { return value(); }
};

} // namespace message_traits
} // namespace ros

namespace ros
{
namespace serialization
{

  template<class ContainerAllocator> struct Serializer< ::path_follower::TrajectoryPoint2D_<ContainerAllocator> >
  {
    template<typename Stream, typename T> inline static void allInOne(Stream& stream, T m)
    {
      stream.next(m.t);
      stream.next(m.x);
      stream.next(m.y);
      stream.next(m.theta);
      stream.next(m.kappa);
      stream.next(m.kappa_dot);
      stream.next(m.v);
      stream.next(m.a);
      stream.next(m.jerk);
      stream.next(m.delta_theta);
      stream.next(m.d);
      stream.next(m.a_lat);
    }

    ROS_DECLARE_ALLINONE_SERIALIZER
  }; // struct TrajectoryPoint2D_

} // namespace serialization
} // namespace ros

namespace ros
{
namespace message_operations
{

template<class ContainerAllocator>
struct Printer< ::path_follower::TrajectoryPoint2D_<ContainerAllocator> >
{
  template<typename Stream> static void stream(Stream& s, const std::string& indent, const ::path_follower::TrajectoryPoint2D_<ContainerAllocator>& v)
  {
    s << indent << "t: ";
    Printer<double>::stream(s, indent + "  ", v.t);
    s << indent << "x: ";
    Printer<double>::stream(s, indent + "  ", v.x);
    s << indent << "y: ";
    Printer<double>::stream(s, indent + "  ", v.y);
    s << indent << "theta: ";
    Printer<double>::stream(s, indent + "  ", v.theta);
    s << indent << "kappa: ";
    Printer<double>::stream(s, indent + "  ", v.kappa);
    s << indent << "kappa_dot: ";
    Printer<double>::stream(s, indent + "  ", v.kappa_dot);
    s << indent << "v: ";
    Printer<double>::stream(s, indent + "  ", v.v);
    s << indent << "a: ";
    Printer<double>::stream(s, indent + "  ", v.a);
    s << indent << "jerk: ";
    Printer<double>::stream(s, indent + "  ", v.jerk);
    s << indent << "delta_theta: ";
    Printer<double>::stream(s, indent + "  ", v.delta_theta);
    s << indent << "d: ";
    Printer<double>::stream(s, indent + "  ", v.d);
    s << indent << "a_lat: ";
    Printer<double>::stream(s, indent + "  ", v.a_lat);
  }
};

} // namespace message_operations
} // namespace ros

#endif // PATH_FOLLOWER_MESSAGE_TRAJECTORYPOINT2D_H
