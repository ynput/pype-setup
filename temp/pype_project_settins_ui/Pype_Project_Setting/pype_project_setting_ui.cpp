#include "pype_project_setting_ui.h"
#include "ui_pype_project_setting_ui.h"

Pype_project_setting_ui::Pype_project_setting_ui(QWidget *parent) :
    QWidget(parent),
    ui(new Ui::Pype_project_setting_ui)
{
    ui->setupUi(this);
}

Pype_project_setting_ui::~Pype_project_setting_ui()
{
    delete ui;
}
