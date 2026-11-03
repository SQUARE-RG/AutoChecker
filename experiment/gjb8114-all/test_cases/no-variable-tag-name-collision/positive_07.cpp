#include <cstdint>

struct Settings
{
    int volume;
};

int main()
{
    Settings config;
    Settings &settingsRef = config;
    settingsRef.volume = 1;
    return 0;
}
