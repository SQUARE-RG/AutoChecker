#include <iostream>
#include <string>

// Globals are only declared here; no initializer is written at namespace scope.
std::string gAppName;
int gLogLevel;
bool gInitialized;

// Centralized initialization module: the single place where globals receive
// their values.
void InitializeGlobals() {
    gAppName = "ucassaat-demo";
    gLogLevel = 2;
    gInitialized = true;
}

int main() {
    InitializeGlobals();
    if (!gInitialized) {
        return 1;
    }
    std::cout << gAppName << " log-level=" << gLogLevel << '\n';
    return 0;
}
