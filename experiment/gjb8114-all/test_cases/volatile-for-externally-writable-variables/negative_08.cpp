#include <thread>

class DeviceStatus {
public:
    static int external_count;
};

int DeviceStatus::external_count = 0;  // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-13-12]

void external_writer() {
    DeviceStatus::external_count = 1;
}

int main() {
    std::thread writer(external_writer);
    writer.join();
    return DeviceStatus::external_count;
}
