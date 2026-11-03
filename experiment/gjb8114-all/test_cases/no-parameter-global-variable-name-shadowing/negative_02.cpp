#include <string>

std::string profile_name = "default";

int apply_profile(const std::string& profile_name) // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-13-2]
{
    return static_cast<int>(profile_name.size());
}

int main()
{
    return apply_profile("guest");
}
