//  SELECT PART  
PART = "both"; // ["bottom","top","both"]

//  MAIN PCB DIMENSIONS
board_len = 65.53;         // x
board_wid = 30;            // y
board_thk = 1.6;           // PCB thickness

// Tallest components (above PCB top / below PCB bottom)
comp_bottom = 3.0;
comp_top    = 12.1;        // approx 0.54" total - 1.6 mm PCB

//  PLASTIC THICKNESSES AND CLEARANCES 
wall  = 2.0;
floor = 2.0;
lid   = 2.0;

clear_xy = 0.6;            // side clearance
clear_z  = 0.6;            // vertical breathing room

//  USB PORT 1
// NOTE: "short" => long X wall; "long" => short Y wall (the PCB end)
usb_present = true;
usb_is_typeC = true;       // set false if you switch to USB A sizes
usb_side = "long";
usb_offset_from_left = 21;
usb_wall_clearance   = 0.40;

// USB PORT 2 (Micro USB)
usb2_present = true;
usb2_is_typeC = false;     // micro
usb2_side = "long";
usb2_offset_from_left = 5;
usb2_wall_clearance   = 0.40;

// USB shell sizes
usbC_w=12.0;  usbC_h=4.5;  usbC_depth=6.5;
micro_w=7.6; micro_h=2.9; micro_depth=6.0;

//  SMA ANTENNA 
antenna_bulkhead = true;
sma_on_short_side   = true;        // true => long X wall, false => short Y wall
sma_offset_from_left = 16;
sma_hole_d   = 7.8;                // close to barrel diameter
sma_pocket_d = sma_hole_d + 2;     // width of the U pocket (circle and slot)
sma_flat_clear = 11.0;             // kept for possible hex recess later

//  VENTING 
side_vents = false;
lid_vents  = true;
vent_slot  = [1.2, 12];
vent_pitch = 4.0;

//  LID LIP (filled lid with overlap) 
lid_rabbet_depth = 1.0;
lid_rabbet_clear = 0.25;

//  STANDOFFS AND MOUNTING 
standoff_h=5.0;
standoff_d=5.0;
insert_hole_d=3.6;         // for M2.5 heat set insert
through_hole_d=2.6;        // M2.5 clearance

hole_inset=3.0;
mount_holes=[
  [hole_inset,            hole_inset],
  [board_len-hole_inset,  hole_inset],
  [board_len-hole_inset,  board_wid-hole_inset],
  [hole_inset,            board_wid-hole_inset]
];

//  DERIVED DIMENSIONS 
inner_len = board_len + 2*clear_xy;
inner_wid = board_wid + 2*clear_xy;
body_len  = inner_len + 2*wall;
body_wid  = inner_wid + 2*wall;

base_cavity = floor + standoff_h + board_thk + comp_top + clear_z;
lid_inner   = lid;
body_ht     = base_cavity + lid_inner;

//  Toggles (preview helpers) 
show_pcb_preview = true;   // set false to hide green board
show_usb_markers = false;  // set true to see small spheres at USB centers


//
// Helpers
//
module horiz_slot(len,wid,thk){ cube([len,wid,thk],center=true); }
module pcb_outline(){ cube([board_len,board_wid,board_thk],center=false); }

module standoff(pos,through=false){
  translate([wall+clear_xy+pos[0], wall+clear_xy+pos[1], floor])
  difference(){
    cylinder(h=standoff_h,d=standoff_d,$fn=40);
    translate([0,0,-0.1])
      cylinder(h=standoff_h+0.2, d=(through?through_hole_d:insert_hole_d), $fn=28);
  }
}

//  Rounded rectangle helpers (for USB openings) 
module _roundrect_2d(w,h,r){
  r = min(r, w/2, h/2);
  offset(r=r) square([w-2*r, h-2*r], center=true);
}
module rr_y(w,h,thk,r){ // through Y (long X wall)
  rotate([90,0,0])
    linear_extrude(height=thk, center=true)
      _roundrect_2d(w,h,r);
}
module rr_x(w,h,thk,r){ // through X (short Y wall)
  rotate([0,90,0])
    linear_extrude(height=thk, center=true)
      _roundrect_2d(w,h,r);
}
micro_corner_r = 0.6;
usbC_corner_r  = 1.2;


// USB CUTOUTS (two ports)

module usb_cutout_port(is_typeC, side, offset_from_left, wall_clear){
  usb_w   = is_typeC ? usbC_w : micro_w;
  usb_h   = is_typeC ? usbC_h : micro_h;
  depth   = is_typeC ? usbC_depth : micro_depth;
  slack_w = usb_w + 2*wall_clear;
  slack_h = usb_h + 2*wall_clear;
  cr      = is_typeC ? usbC_corner_r : micro_corner_r;
  flare   = 0.6; // inside relief

  if (side=="short"){ // long X wall => extrude along Y
    x = offset_from_left + wall;
    z = floor + standoff_h + board_thk/2;
    translate([x,-0.01,z]) rr_y(slack_w,slack_h,wall+0.02,cr);
    translate([x, wall + depth/2, z]) rr_y(slack_w+flare,slack_h+flare,depth+2,cr+0.3);
  } else {            // short Y wall => extrude along X
    y = offset_from_left + wall;
    z = floor + standoff_h + board_thk/2;
    translate([-0.01,y,z]) rr_x(slack_h,slack_w,wall+0.02,cr);
    translate([wall + depth/2, y, z]) rr_x(slack_h+flare,slack_w+flare,depth+2,cr+0.3);
  }
}

module usb_cutouts(){
  if (usb_present)
    usb_cutout_port(usb_is_typeC, usb_side, usb_offset_from_left, usb_wall_clearance);
  if (usb2_present)
    usb_cutout_port(usb2_is_typeC, usb2_side, usb2_offset_from_left, usb2_wall_clearance);
}

// Optional USB center markers
module _usb_center_markers(){
  z = floor + standoff_h + board_thk/2;
  if (usb_present){
    if (usb_side=="short")
      translate([usb_offset_from_left+wall, wall/2, z]) color("red") sphere(d=1.8);
    else
      translate([wall/2, usb_offset_from_left+wall, z]) color("red") sphere(d=1.8);
  }
  if (usb2_present){
    if (usb2_side=="short")
      translate([usb2_offset_from_left+wall, wall/2, z]) color("lime") sphere(d=1.8);
    else
      translate([wall/2, usb2_offset_from_left+wall, z]) color("lime") sphere(d=1.8);
  }
}
if (show_usb_markers) %_usb_center_markers();


// SMA HOLE with U pocket

module sma_hole() {
  if (antenna_bulkhead) {

    // vertical center of SMA
    sma_z = floor + standoff_h + board_thk + comp_top/2;

    // rectangle width and extra slot height
    slot_w     = sma_pocket_d;
    slot_extra = 0.5;

    if (sma_on_short_side) {
      // long X wall on far (+Y) side

      x = sma_offset_from_left + wall;
      y_center = body_wid - wall/2;   // middle of wall thickness

      // circular pocket
      translate([x, y_center, sma_z])
        rotate([90,0,0])
          cylinder(h = wall + 0.2, d = sma_pocket_d,
                   center = true, $fn = 40);

      // slot that overlaps the upper part of the circle
      slot_z0 = sma_z;                        // through circle center
      slot_h  = body_ht - slot_z0 + slot_extra;

      translate([x - slot_w/2,
                 y_center - wall/2 - 0.01,
                 slot_z0])
        cube([slot_w, wall + 0.02, slot_h], center = false);

    } else {
      // short Y wall on far (+X) side

      y = sma_offset_from_left + wall;
      x_center = body_len - wall/2;

      // circular pocket
      translate([x_center, y, sma_z])
        rotate([0,90,0])
          cylinder(h = wall + 0.2, d = sma_pocket_d,
                   center = true, $fn = 40);

      // slot that overlaps upper part of the circle
      slot_z0 = sma_z;
      slot_h  = body_ht - slot_z0 + slot_extra;

      translate([x_center - wall/2 - 0.01,
                 y - slot_w/2,
                 slot_z0])
        cube([wall + 0.02, slot_w, slot_h], center = false);
    }
  }
}


// Side vents (slots)

module vent_slots_on_wall(short_side=true){
  len    = short_side ? body_len : body_wid;
  usable = len - 20;
  count  = max(0, floor(usable/vent_pitch));
  for(i=[0:count-1]){
    pos = 10 + (i+0.5)/count * usable;
    if(short_side){
      translate([pos,-0.01, body_ht/2])
        rotate([90,0,0]) horiz_slot(vent_slot[1], vent_slot[0], wall+0.02);
    } else {
      translate([-0.01,pos, body_ht/2])
        rotate([0,90,0]) horiz_slot(vent_slot[1], vent_slot[0], wall+0.02);
    }
  }
}


// Lid vents (grid)

module lid_vent_field(){
  if (lid_vents){
    rows = 5;
    cols = max(0, floor((inner_len-20)/vent_pitch));
    for(r=[0:rows-1]) for(c=[0:cols-1]){
      x = wall+10+c*vent_pitch;
      y = wall + inner_wid/2 - (rows/2 - 0.5)*vent_pitch + r*vent_pitch;
      z = body_ht - lid/2;
      translate([x,y,z])
        cube([vent_slot[1], vent_slot[0], lid+0.02], center=true);
    }
  }
}


// Bottom shell

module bottom_shell(){
  difference(){
    cube([body_len,body_wid,body_ht],center=false); // outer
    translate([wall,wall,lid])
      cube([inner_len,inner_wid,body_ht-lid],center=false); // inner cavity

    usb_cutouts();
    if(side_vents){
      vent_slots_on_wall(true);
      vent_slots_on_wall(false);
    }
    sma_hole();
  }

  // standoffs
  for(p=mount_holes) standoff(p,false);

  // PCB preview
  if (show_pcb_preview)
    %color([0,1,0,0.15])
      translate([wall+clear_xy, wall+clear_xy, floor+standoff_h])
        pcb_outline();
}


// Top lid

module top_lid(){
  difference(){
    translate([0,0,body_ht-lid])
      cube([body_len,body_wid,lid],center=false);

    translate([wall - lid_rabbet_clear,
               wall - lid_rabbet_clear,
               body_ht - lid - 0.01])
      cube([inner_len + 2*lid_rabbet_clear,
            inner_wid + 2*lid_rabbet_clear,
            lid_rabbet_depth + 0.02], center=false);

    for(p=mount_holes)
      translate([wall+clear_xy+p[0], wall+clear_xy+p[1], body_ht-lid-0.01])
        cylinder(h=lid+0.02, d=through_hole_d, $fn=28);

    lid_vent_field();
  }
}


// Render selector

if (PART=="bottom")       color("gainsboro") bottom_shell();
else if (PART=="top")     color("white")     top_lid();
else { color("gainsboro") bottom_shell(); color([1,1,1,0.35]) top_lid(); }
