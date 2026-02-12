
def make_scaled_biomechanical_models(table_name, save_directory, model_naming_pattern):
    # step 1: load table and process it
    # step 2: for each subject compute BSIP from table (Dumas, 2018)
    # step 3: for each subject make MuJoCo XML file with adequate BSIPs saved in given directory (e.g., .\models) and for each subject save according to naming pattern options name and subject number
    # e.g. subj_{name}_{number}.xml
    # e.g. {number}.xml
    # step 3a: if subject is male -> rgba = blue female -> rgba = pink
    # step 4: profit

    pass


# step 3 details
"""
Optional function arguments:
    Include joint limits (flag)
    Full dofs (flag)
        DoF exclusion specifier (List[str]: ['abdomen flexion', 'abdomen rotation'])

    
Bodies:
    r_foot
        parent: r_shank
        joint type: hinge x2 (add only plantar/dorsiflexion, will add ankle eversion/inversion)
    r_shank
        parent: r_thigh
        joint type: hinge
    r_thigh
        parent: pelvis
        joint type: ball
    pelvis
        parent: abdomen
        joint type: ball
    abdomen
        parent: torso
        joint type: ball
    torso
        parent: worldbody
        joint type: free
    head
        parent: torso
        joint type: ball
    r_upper_arm
        parent: torso
        joint type: ball
    r_forearm
        parent: r_upper_arm
        joint type: hinge (will add elbow rotation)
    r_hand
        parent: r_forearm
        joint type: hinge x2 (add only flexion/extension, will add ulnar/radial deviation later)

    all with prefix r_ also exist with prefix l_

    root_body == torso

"""
make_scaled_biomechanical_models("Anthropometry.xlsx")
