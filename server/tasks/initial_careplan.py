from crewai import Task

from agents.main import physician


def initial_careplan(age, sex, chat):
    task = Task(
        description=f"""
----
Care Plan Instructions
----
You are a primary care physician tasked with writing a care plan, which lists the
next steps in care management that the patient and the physician will perform. Categorize the next steps into five sections: Medications, Referrals, Tests,
Lifestyle and Supportive Care. Definitions and scopes of each section are defined below.

Medications:
// Definition of section

Referrals:
// Definition of section

Tests:
// Definition of section

Lifestyle:
// Definition of section

Supportive Care:
// Definition of section

Example of a Care Plan:
Medications:
(1) Prescribe an appropriate antibiotic, such as nitrofurantoin, fosfomycin, or trimethoprim/sulfamethoxazole,
to treat the infection. Note that the choice of antibiotic may be adjusted based on the results of the urine culture.
(2) Continue the use of over-the-counter pain relief medication, such as AZO, until the antibiotic treatment relieves symptoms.

Referrals:
(1) If symptoms worsen or do not improve after a few days of antibiotic treatment, refer the patient to ...

Tests:
(1) Perform a urinalysis and urine culture to confirm the presence of a urinary tract infection and to identify ...

Lifestyle:
(1) Encourage the patient to increase fluid intake, particularly water, to help flush out bacteria from the urinary tract.
(2) Suggest urinating frequently and fully emptying the bladder to help clear the infection.
(3) Recommend proper hygiene practices, such as ...
(4) Advise the use of a urinary health supplement ...

Supportive Care:
(1) Provide education on recognizing the signs and symptoms of recurrent urinary tract infections and the
importance of seeking timely medical care.
(2) Offer reassurance and support regarding the patient's mental health and ...

----
Care Plan Instructions
----
Now that you've seen an example, you will now write a care plan of the same format (
five sections: Medications, Referrals, Tests, Lifestyle and Supportive Care).
The dialogue you will use to write a care plan about is a medical encounter between
a {age} and {sex} patient and a doctor done over chat:
----
Dialogue
----
{chat}
----
Care Plan
----
""",
        expected_output="a care plan of the same format (five sections: Medications, Referrals, Tests, Lifestyle and Supportive Care)",
        agent=physician,
    )

    return task
