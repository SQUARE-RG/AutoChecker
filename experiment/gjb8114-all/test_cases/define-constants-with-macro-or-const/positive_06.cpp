#include <string>

const std::string kReadyStatus = "READY";

bool isReadyStatus(const std::string& status) {
  return status == kReadyStatus;
}
