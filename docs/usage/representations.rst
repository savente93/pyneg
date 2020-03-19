.. representations:

Representations of necessary components
========================================

Negotiaion Space
   Various components of the library need to be aware of the entire negotiaion space for consistency. THe negotiation space is represented by an object of type :code:`Dict[str,List[str]]`. Meaning that it is represented as a dictionary with issue names as keys, and a list of possible values. e.g.

   .. code::
      
      {
         "Salary": ["2000", "4000"], 
         "HoursPerWeek": ["30", "34", "38"],   
         "VacationDaysPerYear": ["20", "24", "28"], 
         "CompanyCar": ["Yes", "No"]
      }

   Note that everything is represented as a string because of compatability reasons with ProbLog, and also that they have no impact or meaning beyond what is specified by the utility function. Note that for compatability reasons both issues and values must either be represented by strings or have a stable and unique string representation. 

Utility Function
   Utility functions are represented as atomic dictionaries. that means they are indexed by strings of issue value pairs in the format: :code:`"issue_value"`. For this reason neither issue nor value names can include underscores or spaces. The dictionary values should be the reward the agents will get for that assignment. For example, in the running senario a utililty of 1000 for the assignment of 4000 to the Salary would be represented as :code:`{"Salary_4000":1000.0}`. 

Offers
   Offers can be represented in two formats: Atomic and Nested. 
      Atomic 
         Atomic offers are dictionaries with keys of the form :code:`"issue_value"`. There should be exactly one entry per issue value assignment and the values should be either 1.0 or 0.0. This format is used to communicate with ProbLog and to calculate the utilities. For example:
         
         .. code::
            
            Offer({
                     "Salary_2000":0.0, "Salary_4000":1.0, 
                     "HoursPerWeek_30":0.0, "HoursPerWeek_34":0.0, "HoursPerWeek_38":1.0,   
                     "VacationDaysPerYear_20":0.0, "VacationDaysPerYear_24":0.0, "VacationDaysPerYear_28":1.0, 
                     "CompanyCar_Yes":1.0, "CompanyCar_No":0.0
                  })
      Nested 
         Nested offers are dictionaries that are indexed by the issues and the outher dictionary values are again dictionaries with values as keys. The inner dictionary values should agian be either 1.0 or 0. For example:
         
         .. code::
      
            Offer({
               "Salary": {"2000":0.0, "4000":1.0}, 
               "HoursPerWeek": {"30":0.0, "34":0.0, "38":1.0},   
               "VacationDaysPerYear": {"20":0.0, "24":0.0, "28":1.0}, 
               "CompanyCar": {"Yes":1.0, "No":0.0}
            })


Issue weights
   Because everything else is represented using dictionaries and they don't have stable soring, issue weights are also represented as dictionaries, indexed by issueS. The dictionary values should form a distribution.

Knowledge bases
   Knowledge bases are represented as lists of strings. Each string should be exactly one valid ProbLog statement. Additionally note that assignements should be represented as atomicFor example, if 38 hours is considered fulltime employment and fulltime employment must be payed 4000 that could be represented as :code:`["fulltime :- HoursPerWeek_38", "Salary_4000 :- fulltime"]`

Reservation values
   Reservation values represent the minimal utility required for an agent to accept an offer. Currently agents will accept the first offer that has utlity greater than the reservation value. The reservation value should be represented as a float between 0.0 and 1.0. This is the percentage of the maximum utility and agetn can get. The factory will calculate the optimal value and set the absolute reservation value accordingly. 