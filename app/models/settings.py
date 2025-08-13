from ..extensions import db


class GlobalSettings(db.Model):
    """
    Minimal global settings used by costing, etc.
    Currently just burden percent so existing code that imports
    GlobalSettings keeps working unchanged.
    """
    id = db.Column(db.Integer, primary_key=True)
    burden_percent = db.Column(db.Float, nullable=False, default=0.0)

    def __repr__(self) -> str:
        return f"<GlobalSettings burden_percent={self.burden_percent}>"


class AppSetting(db.Model):
    """
    App-level settings for overtime/doubletime rules used by Admin UI.
    These are the exact fields your app tries to create on startup.
    """
    id = db.Column(db.Integer, primary_key=True)

    # When hours in a single day exceed this threshold, pay overtime
    overtime_threshold_hours_per_day = db.Column(db.Integer, nullable=False, default=8)

    # Multiplier used for overtime hours (e.g., 1.5x)
    overtime_multiplier = db.Column(db.Float, nullable=False, default=1.5)

    # When hours in a single day exceed this threshold, pay doubletime
    doubletime_threshold_hours_per_day = db.Column(db.Integer, nullable=False, default=12)

    # Multiplier used for doubletime hours (e.g., 2.0x)
    doubletime_multiplier = db.Column(db.Float, nullable=False, default=2.0)

    def __repr__(self) -> str:
        return (
            "<AppSetting ot_thresh={ot} ot_mult={om} dt_thresh={dt} dt_mult={dm}>"
            .format(
                ot=self.overtime_threshold_hours_per_day,
                om=self.overtime_multiplier,
                dt=self.doubletime_threshold_hours_per_day,
                dm=self.doubletime_multiplier,
            )
        )
