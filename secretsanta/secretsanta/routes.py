import random
from secretsanta import app, db
from flask import render_template, redirect, request, url_for, flash
from secretsanta.models import User, Event, EventMembers,EventFields,UserEventFields,GiverReceivers
from secretsanta.forms import RegisterForm, LoginForm, EventForm, AddUserEvent,FieldsForm, UpdateUserFieldsForm,UserFieldsForm
from flask_login import login_user, logout_user, login_required, current_user
from datetime import datetime
#flask_login helps with determining the current user, this is why we're able to use the variable current_user without declaring it in html

@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"),404


@app.route("/")
@app.route("/home")
def home_page():
    return render_template('home.html')


def get_receiver_member(event):
    person_to_receive=GiverReceivers.query.filter_by(event_id=event, giver_id=current_user.id).first()
    
    return person_to_receive.receiver_id





@app.route("/dashboard")
@login_required
def dashboard_page():
    user_events=EventMembers.query.filter_by(user_id=current_user.id,status='member').all()
    
    return render_template('dashboard.html',user_events=user_events,get_receiver_member=get_receiver_member)




def is_user_member(event, current_user):
    for person in event.members:
        if person.user_id == current_user.id and person.status == 'member':
            return 'member'
        elif person.user_id == current_user.id and person.status == 'pending':
            return 'pending'
    return 'none'

@app.route("/events")
@login_required
def events_page():
    events=Event.query.filter_by(event_status='open').order_by(Event.event_status.desc(), Event.event_id.desc()).all()
    return render_template('events.html', events=events, is_user_member=is_user_member)


@app.route("/request-person-info/eventID=<int:event_id>/person=<int:person_id>", methods=['GET','POST'])
@login_required
def secret_info(event_id,person_id):

    if not GiverReceivers.query.filter_by(event_id=event_id, giver_id=current_user.id, receiver_id=person_id).first():
        flash ('You don\'t have access to view this user\'s information!.', category='danger')
        return redirect(url_for('event_info', event_id=event_id))



    person_fields=UserEventFields.query.filter_by(event_id=event_id,user_id=person_id).first()
    selected_person=User.query.filter_by(id=person_id).first()

    return render_template('secretinfo.html', person_fields=person_fields, selected_person=selected_person)



@app.route("/request_event/eventID=<int:event_id>/member=<int:member_id>", methods=['GET','POST'])
@login_required
def request_event(event_id,member_id):
        try:
            if EventMembers.query.filter_by(user_id=member_id, event_id=event_id, status='pending').first():
                flash('You already requested this event.', category='danger')
                return redirect(url_for('events_page'))
            if EventMembers.query.filter_by(user_id=member_id, event_id=event_id, status='member').first():
                flash('You\'re already a member of this event.', category='danger')
                return redirect(url_for('events_page'))
            if Event.query.filter_by(event_id=event_id, event_status='closed').first():
                flash('This event is closed! Sorry!', category='danger')
                return redirect(url_for('events_page'))
            
            user_to_add=EventMembers(user_id=member_id,event_id=event_id,status='pending')
            db.session.add(user_to_add)
            db.session.commit()
            flash('Request Successfull!', category='success')

        except:
            flash('Event Doesn\'t exist. Please Try A Different Event', category='danger')
            return redirect(url_for('events_page'))
        
        return redirect(url_for('events_page'))

@app.route("/cancel_request/eventID=<int:event_id>", methods=['GET','POST'])
@login_required
def cancel_request(event_id):
        member_to_cancel=EventMembers.query.filter_by(user_id=current_user.id, event_id=event_id, status='pending')
        if member_to_cancel.first().status=='pending':
            try:
                member_to_cancel.delete()
                db.session.commit()
                flash('Request Successfully removed!', category='success')

            except:
                flash('Error Cancelling Event!', category='danger')
                return redirect(url_for('events_page'))
            
        return redirect(url_for('events_page'))


@app.route("/delete_event/<int:event_id>", methods=['GET','POST'])
@login_required
def delete_event(event_id):
    event_to_delete=Event.query.get_or_404(event_id)
    giver_receivers=GiverReceivers.query.filter_by(event_id=event_id)
    if current_user.id == event_to_delete.coordinator_id:
        try:
            if giver_receivers:
                giver_receivers.delete()

            EventMembers.query.filter_by(event_id=event_id).delete()
            EventFields.query.filter_by(event_id=event_id).delete()
            UserEventFields.query.filter_by(event_id=event_id).delete()
            db.session.delete(event_to_delete)
            db.session.commit()
            flash('Successfully Deleted Event!', category='success')
        except Exception as e:
            print(e)
            db.session.rollback()
            flash('Error deleting event. Please try again.', category='danger')
    else:
        flash('You do not have permission to delete this event.', category='danger')
    return redirect(url_for('events_page'))






@app.route("/delete_member/member=<int:member_id>/id=<int:event_id>", methods=['GET','POST'])
@login_required
def delete_member(member_id,event_id):
    event_to_delete_from=Event.query.get_or_404(event_id)
    if current_user.id == event_to_delete_from.coordinator_id:
        try:
            EventMembers.query.filter_by(event_id=event_id, user_id=member_id).delete()
            db.session.commit()
            flash('Successfully Deleted member!', category='success')
        except Exception as e:
            print(e)
            db.session.rollback()
            flash('Error deleting member. Please try again.', category='danger')
    else:
        flash('You do not have permission to delete this member.', category='danger')
    return redirect(url_for('event_info', event_id=event_id))





@app.route("/add-participant-info/id=<int:event_id>", methods=['GET','POST'])
@login_required
def user_fields_add(event_id):


    status_to_check=EventMembers.query.filter_by(event_id=event_id, user_id=current_user.id).first()
    #Checks if user has access to submit
    if not status_to_check or status_to_check.status != 'member':
        flash('You Do Not Have Access', category='danger')
        return redirect(url_for('event_info', event_id=event_id))
    
    has_entry=UserEventFields.query.filter_by(event_id=event_id,user_id=current_user.id).first()
    #Checks if user can't submit due to already having an entry
    if has_entry:
        flash('You Already Submitted This Form!', category='danger')
        return redirect(url_for('event_info', event_id=event_id))
    
    if request.method == 'POST':
        userfieldsform = UserFieldsForm()
        
        field=EventFields.query.filter_by(event_id=event_id).first()
        person_fields_to_add = UserEventFields(field_id=field.id,
                                                event_id=event_id,
                                                user_id=current_user.id,
                                                field_1=userfieldsform.field_1.data,
                                                field_2=userfieldsform.field_2.data,
                                                field_3=userfieldsform.field_3.data,
                                                field_4=userfieldsform.field_4.data,
                                                field_5=userfieldsform.field_5.data,
                                                field_6=userfieldsform.field_6.data,
                                                field_7=userfieldsform.field_7.data,
                                                field_8=userfieldsform.field_8.data,
                                                field_9=userfieldsform.field_9.data,
                                                field_10=userfieldsform.field_10.data
                                                )
        db.session.add(person_fields_to_add)
        db.session.commit()
        flash('Info Added Successfully!', category='success')
        
        
        #The if statement below works, but isn't convenient for this part because some events might not use all 10 fields and the DataRequired() validator will not allow the db to be updated
        #if userfieldsform.validate_on_submit():
        #else:
            #flash(userfieldsform.errors, category='danger')
    return redirect(url_for('event_info', event_id=event_id))















@app.route("/update-participant-info/id=<int:event_id>", methods=['GET','POST'])
@login_required
def user_fields_update(event_id):
    field_to_delete=UserEventFields.query.filter_by(event_id=event_id, user_id=current_user.id).first()

    if request.method == 'POST' and field_to_delete.user_id==current_user.id:
        updateuserinfo=UpdateUserFieldsForm()

        field_to_delete=UserEventFields.query.filter_by(event_id=event_id, user_id=current_user.id).first()

        fields_to_add=UserEventFields(
                                  field_id=field_to_delete.field_id,
                                  event_id=event_id,
                                  user_id=current_user.id,
                                  field_1=updateuserinfo.field_1.data,
                                  field_2=updateuserinfo.field_2.data,
                                  field_3=updateuserinfo.field_3.data,
                                  field_4=updateuserinfo.field_4.data,
                                  field_5=updateuserinfo.field_5.data,
                                  field_6=updateuserinfo.field_6.data,
                                  field_7=updateuserinfo.field_7.data,
                                  field_8=updateuserinfo.field_8.data,
                                  field_9=updateuserinfo.field_9.data,
                                  field_10=updateuserinfo.field_10.data)
        
        
        db.session.delete(field_to_delete)
        db.session.add(fields_to_add)
        db.session.commit()
        flash('Fields updated Successfully!', category='success')
        return redirect(url_for('event_info', event_id=event_id))
    else:
        flash('You can\'t update the fields of another person!', category='danger')
        return redirect(url_for('event_info', event_id=event_id))















@app.route("/event-info/id=<int:event_id>", methods=['GET','POST'])
@login_required
def event_info(event_id):
    event = Event.query.filter_by(event_id=event_id).first()
    event_pending = EventMembers.query.filter_by(event_id=event_id,status='pending').first()
    event_fields = EventFields.query.filter_by(event_id=event_id).first()
    member_status = EventMembers.query.filter_by(event_id=event_id,user_id=current_user.id,status='member').first()
    person_info = UserEventFields.query.filter_by(event_id=event_id,user_id=current_user.id).first()
    giving = GiverReceivers.query.filter_by(event_id=event_id, giver_id=current_user.id).first()
    

    if not event:
        flash('Event not found.', category='danger')
        return redirect(url_for('events_page'))
    
    form=AddUserEvent()
    fieldform=FieldsForm()
    userfieldsform=UserFieldsForm()
    updateuserinfo=UpdateUserFieldsForm()

    if form.validate_on_submit():
        try:
            user = User.query.filter_by(username=form.username.data.lower()).one()
        except:
            flash('User not found.', category='danger')
            return redirect(url_for('event_info', event_id=event_id))
        
        if EventMembers.query.filter_by(user_id=user.id, event_id=event_id).first():
            flash('User is already a member of the event.', category='danger')
            return redirect(url_for('event_info', event_id=event_id))
        
        
        user_to_add=EventMembers(user_id=user.id,
                                 event_id=event_id,
                                 status='member')
        db.session.add(user_to_add)
        db.session.commit()
        flash('User Added Successfully!', category='success')
        if form.errors !={}: #If there are not no errors from the validation
            for err_msg in form.errors.values():
                flash(f'There was an error!: {err_msg}', category='danger')
                
                
    if fieldform.validate_on_submit():
        fields_to_add=EventFields(event_id=event_id,
                                  field_1=fieldform.field_1.data,
                                  field_2=fieldform.field_2.data,
                                  field_3=fieldform.field_3.data,
                                  field_4=fieldform.field_4.data,
                                  field_5=fieldform.field_5.data,
                                  field_6=fieldform.field_6.data,
                                  field_7=fieldform.field_7.data,
                                  field_8=fieldform.field_8.data,
                                  field_9=fieldform.field_9.data,
                                  field_10=fieldform.field_10.data)
        
        db.session.add(fields_to_add)
        db.session.commit()
        flash('Fields Added Successfully!', category='success')
        return redirect(url_for('event_info', event_id=event_id))
    
    
        
    
    return render_template("info.html",event=event, form=form, event_pending=event_pending, 
                           event_fields=event_fields, fieldform=fieldform, userfieldsform=userfieldsform,
                           member_status=member_status, person_info=person_info, 
                           giving=giving,updateuserinfo=updateuserinfo)




@app.route("/create", methods=['GET','POST'])
@login_required
def create_event():
    form = EventForm()
    if form.validate_on_submit():
        current_date = datetime.utcnow().date()
        event_to_create=Event( coordinator_id=current_user.id,
                                event_name=form.event_name.data,
                                event_date=current_date,
                                event_status="open"
                              )
        db.session.add(event_to_create)
        db.session.commit()
        
        member_to_add = EventMembers(user_id=current_user.id,
                                     event_id=event_to_create.event_id,
                                     status='member')
        db.session.add(member_to_add)
        db.session.commit()


        flash('Event Created Successfully!', category='success')
        if form.errors !={}: #If there are not no errors from the validation
            for err_msg in form.errors.values():
                flash(f'There was an error with creating your event: {err_msg}', category='danger')
        return redirect(url_for('event_info', event_id=event_to_create.event_id))

    return render_template('create.html', form=form)



@app.route("/register", methods=['GET','POST'])
def register_page():
    form = RegisterForm()


    if form.validate_on_submit():
        
        
        
        if User.query.filter_by(username=form.username.data.lower()).first():
             flash(f' Error Username already exists!', category='danger')
             return redirect(url_for('register_page'))
        
        user_to_create=User(username=form.username.data.lower(),
                            first_name=form.first_name.data,
                            last_name=form.last_name.data,
                            email_address=form.email_address.data,
                            password=form.password1.data)
        
        db.session.add(user_to_create)
        db.session.commit()

        login_user(user_to_create)
        flash(f'Account Created Successfully! You are now logged in as {user_to_create.username}', category='success')
        return redirect(url_for('dashboard_page'))
    
    #If one of the validations fails, the error will be stored in form.errors as a dictionary
    if form.errors !={}: #If there are not no errors from the validation
        for err_msg in form.errors.values():
            flash(f'There was an error with creating your account: {err_msg}', category='danger')

    return render_template('register.html',form=form)

@app.route('/login', methods=['GET','POST'])
def login_page():
    form = LoginForm()
    if form.validate_on_submit():
        attempted_user = User.query.filter_by(username=form.username.data.lower()).first()
        attempted_user_email = User.query.filter_by(email_address=form.username.data).first()

        if (attempted_user and attempted_user.check_password_correction(attempted_password=form.password.data)) :
            login_user(attempted_user)
            flash(f'Success! You are logged in as: {attempted_user.username}', category='success')
            return redirect(url_for('dashboard_page'))
        
        #This allows the user to login using their email as well
        elif (attempted_user_email and attempted_user_email.check_password_correction(attempted_password=form.password.data)):
            login_user(attempted_user_email)
            flash(f'Success! You are logged in as: {attempted_user_email.username}', category='success')
            return redirect(url_for('dashboard_page'))
        
        else:
            flash('Username and password are not a match! Please try again', category='danger')

    return render_template('login.html', form=form)


@app.route('/logout')
def logout_page():
    logout_user()
    flash('You have been logged out!', category='info')
    return redirect(url_for("home_page"))




@app.route("/accept_member/member=<int:member_id>/id=<int:event_id>", methods=['GET','POST'])
@login_required
def accept_member(member_id,event_id):
    event_to_delete_from=Event.query.get_or_404(event_id)
    if current_user.id == event_to_delete_from.coordinator_id:
        try:
            member_to_update=EventMembers.query.filter_by(event_id=event_id, user_id=member_id).first()
            member_to_update.status='member'
            db.session.commit()
            flash('Successfully added member!', category='success')

        except Exception as e:
            print(e)
            db.session.rollback()
            flash('Error accepting member. Please try again.', category='danger')
    else:
        flash('You do not have permission to add this member.', category='danger')
    return redirect(url_for('event_info', event_id=event_id))

@app.route("/decline_member/member=<int:member_id>/id=<int:event_id>", methods=['GET','POST'])
@login_required
def decline_member(member_id,event_id):
    event_to_delete_from=Event.query.get_or_404(event_id)
    if current_user.id == event_to_delete_from.coordinator_id:
        try:
            EventMembers.query.filter_by(event_id=event_id, user_id=member_id).delete()
            db.session.commit()
            flash('Successfully Declined Member!', category='success')
        except Exception as e:
            print(e)
            db.session.rollback()
            flash('Error declining member. Please try again.', category='danger')
    else:
        flash('You do not have permission to Decline this member.', category='danger')
    return redirect(url_for('event_info', event_id=event_id))




@app.route("/leave-event/event=<int:event_id>", methods=['GET','POST'])
@login_required
def leave_event(event_id):


    try:
        EventMembers.query.filter_by(event_id=event_id, user_id=current_user.id).delete()
        UserEventFields.query.filter_by(event_id=event_id, user_id=current_user.id).delete()
        db.session.commit()
        flash('Successfully Left Event!', category='success')
    except Exception as e:
        print(e)
        db.session.rollback()
        flash('Error leaving event. Please try again.', category='danger')

    return redirect(url_for('event_info', event_id=event_id))



@app.route("/start_event/id=<int:event_id>", methods=['GET','POST'])
@login_required
def start_event(event_id):
    
    people= [ person.user_id for person in EventMembers.query.filter_by(event_id=event_id, status='member').all()]
    
    if GiverReceivers.query.filter_by(event_id=event_id).first():
        flash('This event has already started!', category='danger')
        return redirect(url_for('event_info', event_id=event_id))
    
    if len(people)<3:
        flash('You do not have enough members to start.', category='danger')
        return redirect(url_for('event_info', event_id=event_id))
        
    event_to_check=Event.query.filter_by(event_id=event_id).first()
    if current_user.id==event_to_check.coordinator_id:
        pairs=dict()
        choices=people[:]
        for i,person in enumerate(people):
            addBack=False
            if person in choices:
                addBack=True
                choices.remove(person)
            if len(choices)==0:
                person_to_swap=random.choice(people[0:len(people)-1])
                pairs[person],pairs[person_to_swap]=pairs[person_to_swap],person
                continue
            choice=random.choice(choices)
            pairs[person]=choice
            choices.remove(choice)
            if addBack:
                choices.append(person)
        try:
            for giver,receiver in pairs.items():
                relationship_to_add=GiverReceivers(event_id=event_id, giver_id=giver, receiver_id=receiver)
                db.session.add(relationship_to_add)
        except:
            flash('Something went wrong, try again!', category='danger')
            return redirect(url_for('event_info', event_id=event_id))
            
        event_to_update=Event.query.filter_by(event_id=event_id).first()
        event_to_update.event_status='closed'
        db.session.commit()
    else:
        flash('You don\'t have permission to start the event!', category='danger')
        return redirect(url_for('event_info', event_id=event_id))
    
    return redirect(url_for('event_info', event_id=event_id))






