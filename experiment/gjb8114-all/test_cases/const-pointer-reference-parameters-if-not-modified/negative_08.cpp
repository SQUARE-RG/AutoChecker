#include <cstddef>
#include <map>
#include <string>

std::size_t count_entries(std::map<std::string, int>& entries) // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-2-7-2]
{
    return entries.size();
}
