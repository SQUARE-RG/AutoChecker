#include <map>
#include <string>

std::map<std::string, std::string> gConfig;
int gRetryCount;

namespace AppInit {

void LoadDefaults() {
    gConfig["host"] = "127.0.0.1";
    gConfig["port"] = "8080";
    gRetryCount = 3;
}

void Initialize() {
    gConfig.clear();
    LoadDefaults();
}

}  // namespace AppInit

int main() {
    AppInit::Initialize();
    return static_cast<int>(gConfig.size()) + gRetryCount;
}
