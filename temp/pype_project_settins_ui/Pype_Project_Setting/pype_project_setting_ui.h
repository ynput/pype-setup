#ifndef PYPE_PROJECT_SETTING_UI_H
#define PYPE_PROJECT_SETTING_UI_H

#include <QWidget>

namespace Ui {
class Pype_project_setting_ui;
}

class Pype_project_setting_ui : public QWidget
{
    Q_OBJECT

public:
    explicit Pype_project_setting_ui(QWidget *parent = nullptr);
    ~Pype_project_setting_ui();

private:
    Ui::Pype_project_setting_ui *ui;
};

#endif // PYPE_PROJECT_SETTING_UI_H
