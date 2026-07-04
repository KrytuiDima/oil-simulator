class WellLifecycle:
    """
    Manages the 31 stages of the well lifecycle.
    """
    STAGES = [
        "Site Survey & Permitting",
        "Rig Mobilization",
        "Rig Up",
        "Conductor Drilling",
        "Conductor Casing & Cementing",
        "Nipple Up (Diverter)",
        "Surface Hole Drilling",
        "Surface Casing Running",
        "Surface Cementing",
        "Nipple Up (BOP)",
        "BOP Testing",
        "Intermediate I Hole Drilling",
        "Intermediate I Casing Running",
        "Intermediate I Cementing",
        "Intermediate II Hole Drilling",
        "Intermediate II Casing Running",
        "Intermediate II Cementing",
        "Production Hole Drilling",
        "Open Hole Logging",
        "Production Casing / Liner Running",
        "Production Cementing",
        "Well Completion",
        "Nipple Down BOP / Nipple Up Tree",
        "Perforation",
        "Stimulation",
        "Flowback & Testing",
        "Production Operations",
        "Workover / Intervention",
        "Enhanced Oil Recovery",
        "Plug & Abandonment (Temporary)",
        "Final Decommissioning"
    ]

    def __init__(self):
        self.current_stage_index = 0
        self.completed_stages = []

    @property
    def current_stage(self):
        return self.STAGES[self.current_stage_index]

    def next_stage(self):
        if self.current_stage_index < len(self.STAGES) - 1:
            self.completed_stages.append(self.current_stage)
            self.current_stage_index += 1
            return True
        return False

    def is_drilling_active(self):
        """
        Returns True if the current stage involves active drilling.
        """
        drilling_stages = [3, 6, 11, 14, 17] # Indexes for drilling stages
        return self.current_stage_index in drilling_stages

    def get_progress_percent(self):
        return (self.current_stage_index / (len(self.STAGES) - 1)) * 100
