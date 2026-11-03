#include <iostream>

enum class Mode { Off, On, Standby };

int main()
{
    Mode mode = Mode::Standby;
    int result = 0;
    switch (mode) {
        case Mode::Off:
            result = 1;
            break;
        case Mode::On:
            result = 2;
            break;
        case Mode::Standby:
            result = 3;
            break;
    }
    return result;
}
