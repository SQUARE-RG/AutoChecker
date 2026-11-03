#include <cstddef>
#include <string>

std::size_t text_length(std::string& text) { // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-2-7-2]
    return text.size();
}
