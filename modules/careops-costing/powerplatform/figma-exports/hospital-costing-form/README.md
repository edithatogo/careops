# NSW Health Budget Buildup Tool (BBT) – Power Platform Design Pack

This is an updated code bundle derived from the original **Hospital Costing Form** Figma Make export.

The bundle has been advanced to translate the attached NSW Health Budget Buildup Tool workbook into a Power Platform target-state design pack, including:

- BBT-specific operating workflow
- approval BPMN for **M / S / E** roles
- Power App form blueprint replacing `SWInput`
- Dataverse data model
- Power BI / reporting dashboard concept
- workbook-to-platform migration map
- target integration architecture
- security / permissions model
- delivery roadmap and ALM view

## Source grounding used for the update

- Workbook: `BBT-2019.05.10V-NSWH 1.xlsm`
- Data dictionary: `BBT_Data_Dictionary_NSWH.docx`
- Permission seed file: `role_assignments.csv`
- App module pattern reference: `AppModule.xml`

## Running the code

Run `npm i` to install the dependencies.

Run `npm run dev` to start the development server.
