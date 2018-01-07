from flask import Flask, session, redirect
# from functools import wraps
def login_required(f):
    # @wraps
    def nf(*args, **kwargs):
    # def nf(x):
        if session.get("user_id") is None:
            return redirect("/login")
        # f(x)
        return f(*args, **kwargs)
    return nf
