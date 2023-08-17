from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify
from flask_login import login_required, current_user
from . import db
import time

import queue

from .models import Vehicle
from .models import ParkingSlot

main = Blueprint('main', __name__)

cmd2vehicle_queue = queue.Queue()
resfromvehicle_queue = queue.Queue()

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/profile')
@login_required
def profile():
    return render_template('profile.html', name=current_user.name)

@main.route('/vehicle')
@login_required
def vehicle():
    db_user_vehicle = db.session.query(Vehicle).filter(Vehicle.owner_id == current_user.id)    
    return render_template('vehicle.html', 
                           db_user_vehicle = db_user_vehicle)

@main.route('/vehicle/prepare_for_parking', methods=['POST'])
@login_required
def vehicle_prepare_for_parking_post():

    # db_user_vehicle = db.session.query(Vehicle).filter(Vehicle.owner_id == current_user.id)
    #TODO
    license_plate = request.form.get('license_plate')
    available_slot = db.session.query(ParkingSlot).all()
    # print(license_plate)
    
    return render_template('slots.html', 
                           license_plate = license_plate,
                           available_slot = available_slot)

@main.route('/vehicle/parking', methods=['POST'])
@login_required
def vehicle_parking_post():
    license_plate = request.form.get('license_plate')
    parking_slot = request.form.get('parking_slot')

    print(license_plate)
    print(parking_slot)

    # Check if parking slot is available in database
    db_vehicle = db.session.query(Vehicle).filter(Vehicle.license_plate == license_plate).first()
    db_slot = db.session.query(ParkingSlot).filter(ParkingSlot.slot_number == parking_slot).first()
    # if db_chosen_slot.status != "free":

    # Check if vehicle ready
    # if db_vehicle.status == "ready-to-park":
    #     flash('The vehicle is not ready to park !!!')
    #     return redirect(url_for('main.parking'))
    
    if db_slot.vehicle_id != None:
        flash('The chosen parking slot is already selected !!!')
        return redirect(url_for('main.vehicle'))
    
    # Send Cmd
    cmd2vehicle_queue.put({
        "command" : "park",
        "license_plate" : license_plate,
        "parking_slot" : parking_slot,
    })

    #TODO: Check if the vehicle change to on-parking with timeout to retry
    while True:
        db.session.refresh(db_vehicle)
        print(db_vehicle.status)
        if db_vehicle.status == "on-parking":
            return redirect(url_for('main.vehicle'))
        
        time.sleep(3)

@main.route('/vehicle/leaving', methods=['POST'])
@login_required
def vehicle_leaving_post():
    license_plate = request.form.get('license_plate')

    cmd2vehicle_queue.put({
        "command" : "leave",
        "license_plate" : license_plate,
        "parking_slot" : "NoData",
    })

    #TODO: Check if the vehicle change to on-leaving with timeout to retry

    return redirect(url_for('main.vehicle'))


# api for vehicle implement
@main.route('/apiv1/vehicle/command', methods=['GET'])
def vehicle_cmd_get():
    timeout = 30  # Timeout after 30 seconds
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            data = cmd2vehicle_queue.get_nowait()
            return jsonify(data)
        except queue.Empty:
            time.sleep(1)  # Wait for 1 second before checking again
        
    return jsonify({"message": "No data"})

@main.route('/apiv1/vehicle/status', methods=['POST'])
def vehicle_status_post():
    data = request.json
    # resfromvehicle_queue.put(data)

    license_plate = data['license_plate']
    vehicle_status = data['status']

    print(f"{license_plate} : {vehicle_status}")

    # Save to database
    db_vehicle = db.session.query(Vehicle).filter(Vehicle.license_plate == license_plate).first()

    if db_vehicle.status != vehicle_status:
        db_vehicle.status = vehicle_status
        db.session.commit()

    return jsonify({"message": "Done"}), 200

# api for parking slot implement
@main.route('/apiv1/parking_slot/status', methods=['POST'])
def parking_slot_status_post():
    data = request.json
    slot_number = data['parking_slot']
    observed_slot_status = data['status']

    print(f"{slot_number} : {observed_slot_status}")

    # Save to database
    db_slot = db.session.query(ParkingSlot).filter(ParkingSlot.slot_number == slot_number).first()
    if db_slot.status != observed_slot_status:
        db_slot.status = observed_slot_status
        db.session.commit()
    
    
    return jsonify({"message": "Done"}), 200





# test
def get_update_from_somewhere():
    # Simulate getting an update (replace with your actual logic)
    time.sleep(10)
    return {"message": "New update"}

@main.route('/test/long_polling')
def get_update():
    start_time = time.time()

    while time.time() - start_time < 60:  # Poll for a maximum of 60 seconds
        # Check if there's an update to send to the client
        # For example, check for new messages, notifications, etc.
        update = get_update_from_somewhere()  # Replace with your update retrieval logic

        if update:
            return jsonify(update)

        time.sleep(1)  # Wait for 1 second before checking again

    return jsonify({"timeout": True}), 408  # Return a timeout status if no update is available
