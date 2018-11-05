#include "pype_project_setting_ui.h"
#include <QApplication>

int main(int argc, char *argv[])
{
    QApplication a(argc, argv);
    Pype_project_setting_ui w;
    w.show();

    return a.exec();
}
