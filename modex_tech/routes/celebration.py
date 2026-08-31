#!/usr/bin/python3
import traceback
from scheduler import schedule_event
from flask import Blueprint,flash,redirect,render_template,request,url_for
from models import generate_tracking_code,GiftRegistration,send_email  
from flask_login import current_user

celebration_bp = Blueprint('celebration', __name__)

@celebration_bp.route('/celebration')
def celebrate():
    try :
        return render_template("services/register.html")
    except Exception as e:
        traceback.print_exc()
        flash("Flash unexpected error kindly wait for resolve")
        return redirect(url_for("celebration.showcase"))

@celebration_bp.route('/register_gift',methods=["GET", "POST"])
def register_gift():

    if request.method == "POST":
        try:
            sender_email=session.get("username")
            recipient_name = request.form.get("recipient_name")
            recipient_email = request.form.get("recipient_email")
            offer = request.form.get("offer")
            delivery_date = request.form.get("delivery_date")
            message = request.form.get("message")
            link = url_for("gifts.view_gift",user_id=user_id,account=account,_external=True)
            tracking_code = generate_tracking_code(current_user.get_id(),offer)

            gift = GiftRegistration(
                    sender_id=current_user.get_id(),
                    sender_email=sender_email,
                    recipient_name=recipient_name,
                    recipient_email=recipient_email,
                    charges=20.00,  
                    offer=offer,
                    delivery_date=delivery_date,
                    message=message,
                    link=link,
                    status="NotPaid"
                    )
            db.session.add(gift)
            db.session.commit()
            schedule_event(GiftRegistration)
            send_email(sender_email,
                       "Gift Registration",
                       """<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>You have something waiting for you</title>
                       </head><body style="margin:0;padding:0;background:#f4f6fb;font-family:Arial,Helvetica,sans-serif;"><table width="100%" cellpadding="0" cellspacing="0" border="0" style="background:#f4f6fb;padding:40px 15px;">
                       <tr><td align="center"><table width="600" cellpadding="0" cellspacing="0" border="0" style="max-width:600px;width:100%;background:#ffffff;border-radius:18px;overflow:hidden;box-shadow:0 8px 30px rgba(0,0,0,0.08);"><tr>
                       <td align="center" style="background:linear-gradient(135deg,#6c63ff,#8f7cff);padding:45px 30px;"><div style="font-size:42px;margin-bottom:12px;">✨</div><h1 style="margin:0;color:#ffffff;font-size:30px;line-height:1.3;">Something Special Is Waiting</h1>
                       <p style="margin:12px 0 0;color:#eeeaff;font-size:15px;">A little surprise, just for you.</p></td></tr><tr><td style="padding:40px 40px 25px;"><p style="margin:0 0 18px;color:#222;font-size:17px;line-height:1.7;">Hello,</p>
                       <p style="margin:0 0 20px;color:#555;font-size:15px;line-height:1.8;">Someone has prepared something special for you. We've kept the details a secret, but there's only one way to discover what it is.</p>
                       <table width="100%" cellpadding="0" cellspacing="0" style="background:#f7f6ff;border-radius:12px;border-left:4px solid #6c63ff;"><tr><td style="padding:18px 20px;">
                       <p style="margin:0;color:#555;font-size:14px;line-height:1.6;">🎁 <strong style="color:#333;">Your surprise is ready.</strong><br>Click below to reveal it.</p></td></tr></table>
                       <table width="100%" cellpadding="0" cellspacing="0" style="margin-top:30px;"><tr><td align="center">
                       <a href="{{ action_url }}" style="display:inline-block;background:#6c63ff;color:#ffffff;text-decoration:none;font-size:16px;font-weight:bold;padding:16px 38px;border-radius:50px;box-shadow:0 6px 18px rgba(108,99,255,0.35);">✨ Reveal My Surprise</a></td></tr></table><p style="margin:28px 0 0;text-align:center;color:#999;font-size:12px;">Your surprise is just one click away.</p></td>
                       </tr><tr><td align="center" style="background:#fafafa;padding:22px 30px;border-top:1px solid #eeeeee;"><p style="margin:0;color:#999;font-size:12px;">Made with ✨ and a little bit of magic.</p><p style="margin:8px 0 0;color:#bbb;font-size:11px;">© 2026 Your Organization</p></td></tr></table></td></tr></table></body></html>""")
            
            flash("Gift registered successfully.")
            return redirect(url_for("celebration.showcase"))
        
        except Exception as e:
            traceback.print_exc()
            flash("Flash unexpected error kindly wait for resolve")
            return redirect(url_for("celebration.showcase"))
    return redirect(url_for("celebration.celebrate"))
@celebration_bp.route('/view_gift',methods=["GET"])
def view_gift(user_id,account) :
    try:
        if user_id and account:
            result=db.session.query(GiftRegistration).filter(sender_id==user_id,account==account).first()
            if not result :
                flash("flash we cannnot find you gift kindly email us ")
            if result.status!="Paid":
                if result.status=="Terminated":
                    fl_msg="Your gift has expired"
                else:
                    fl_msg="Your gifter has not paid for the gift"
                flash(f"{fl_msg}")
                return redirect(url_for("celebration.showcase"))
            result2=db.successfully.query(Payment.amount).filter(Payment.account_number==account).all()
            confirmation=0  
            for r in result2:
                confirmation=confirmation+ result2
            if current_date.strftime("%d%m%y%H%M") == result.delivery_date.strftime("%d%m%y%H%M") :
                if confirmation==result.amount:
                    if result.offer=="Valentine":
                        return render_template("services/valentines.html",contex=result)
                    elif result.offer=="Birthday":
                        return render_template("services/birthday.html",contex=result)
                    else :
                        return render_template("services/graduation.html",contex=result)
                else :
                    flash("Payment has not be completed")
                    return redirect(url_for("celebration.showcase"))
            else:
                flash("The set delivery date has not been  reached kindly be patient")
                return redirect(url_for("celebration.showcase"))
        else :
            flash("No data entered")
            return redirect(url_for("celebration.showcase"))

    except Exception as e:
        traceback.print_exc()
        flash("Flash unexpected error kindly wait for resolve")
        return redirect(url_for("celebration.showcase"))

@celebration_bp.route("/showcase")
def showcase():
    return render_template("services/showcase.html")
                
