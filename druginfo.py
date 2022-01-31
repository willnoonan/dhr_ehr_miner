#AUTHOR: William Noonan

drug_dict = {'NSAID': ('aspirin', 'ibuprofen', 'naproxen', 'celecoxib', 'diclofenac', 'diflunisal', 'etodolac',
                                 'indomethacin', 'ketoprofen', 'ketorolac', 'nabumetone', 'oxaprozin', 'piroxicam',
                                 'salsalate', 'sulindac', 'tolmetin',),  #xTODO how complete is this list?
             'opioid': ('codone',  'morphine', 'hydromorphone', 'fentanyl', 'codeine','methadone', 'meperidine',
                        'tramadol', 'carfentanil', 'buprenorphine'),
             'proton_pump_inhibitor': ('dexlansoprazole','esomeprazole','lansoprazole','omeprazole','pantoprazole','rabeprazole'),
             'antibiotic': ('amoxicillin', 'clarithromycin'),
             'constipation_drug': ('colace', 'docusate', 'glycol', 'polyethylene', 'alvimopan', 'bisacodyl',
                                   'cascara sagrada', 'lactulose', 'lubiprostone', 'magnesium'),
             'pth': ('teriparatide', 'abaloparatide'),
             'vitamin_d': ('ergocalciferol', 'calcitriol', 'calciferol', 'paricalcitol'), #NOTE: unnecessary for our data file because
             'statin': ('statin'), # statin drugs contain "statin", no need to list them all
             'thyroid_med': ('levothyroxine', 'liothyronine', 'liotrix', 'thyroid'), # this will catch "thyroid dessicated", which is a thyroid drug of interest
             'antidiabetic': ('insulin', 'metformin', 'chlorpropamide', 'glimepiride', 'glipizide', 'glyburide',
                              'tolazamide', 'tolbutamide', 'repaglinide', 'nateglinide', 'rosiglitazone',
                              'pioglitazone', 'acarbose', 'miglitol', 'pramlintide', 'exenatide', 'sitagliptin',
                              'glucagon' ),
             'antihypertensive': ('acebutolol', 'atenolol', 'betaxolol', 'bisoprolol', 'carteolol', 'carvedilol',
                                  'esmolol', 'labetalol', 'metoprolol', 'nadolol', 'nebivolol', 'penbutolol',
                                  'pindolol', 'propranolol', 'timolol', 'clonidine', 'guanabenz', 'guanfacine',
                                  'methyldopa', 'guanadrel', 'mecamylamine', 'diazoxide', 'fenoldopam', 'hydralazine',
                                  'minoxidil', 'nitroprusside', 'amlodipine', 'clevidipine', 'diltiazem', 'felodipine',
                                  'isradipine', 'nicardipine', 'nifedipine', 'nisoldipine', 'verapamil', 'benazepril',
                                  'captopil', 'enalapril', 'fosinopril', 'lisinopril', 'moexipril', 'perindopril',
                                  'quinapril', 'ramipril', 'trandolapril', 'candesartan', 'eprosartan', 'irbesartan',
                                  'losartan', 'olmesartan', 'telmisartan', 'valsartan', 'aliskirin'),
             'diuretic': ('acetazolamide', 'amiloride', 'bendroflumethiazide', 'brinzolamide', 'bumetanide',
                          'chlorothiazide', 'chlorthalidone', 'conivaptan', 'demeclocycline', 'dichlorphenamide',
                          'dorzolamide', 'eplerenone', 'ethacrynic', 'furosemide', 'hydrochlorothiazide',
                          'hydroflumethiazide', 'indapamide', 'mannitol', 'methazolamide', 'methyclothiazide',
                          'metolazone', 'polythiazide', 'quinethazone', 'spironolactone', 'torsemide', 'triamterene',
                          'trichlormethiazide'), #TODO note: interestingly no intersection with antihypertensive values
             }

