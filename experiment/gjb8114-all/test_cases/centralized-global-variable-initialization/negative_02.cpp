#include <string>

std::string PickPrimaryHost();

// Violation: the global is initialized by a function call at namespace scope,
// bypassing the centralized initialization module and introducing a
// static-initialization-order dependency.
std::string gPrimaryHost = PickPrimaryHost(); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-11-2]

std::string PickPrimaryHost() {
    return "alpha";
}

int main() {
    return gPrimaryHost.empty() ? 1 : 0;
}
