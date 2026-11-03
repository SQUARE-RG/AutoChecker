#include <map>
#include <string>

// Violation: this namespace-scope global initializes itself with a dynamic
// initializer list instead of being initialized by the project's centralized
// initialization module.
std::map<std::string, std::string> gLimits = {{"cpu", "2"}, {"memory", "512"}}; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-11-2]

int main() {
    return gLimits.empty() ? 1 : 0;
}
