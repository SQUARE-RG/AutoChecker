#include <string>

bool isReadyStatus(const std::string& status) {
  return status == "READY"; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-1-6]
}
