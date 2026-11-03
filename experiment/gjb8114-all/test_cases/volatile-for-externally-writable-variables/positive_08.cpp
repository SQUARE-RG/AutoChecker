#include <thread>

class DeviceStatus {
public:
    static volatile int external_count;
};

volatile int DeviceStatus::external_count = 0;

void external_writer() {
    DeviceStatus::external_count = 1;
}

int main() {
    std::thread writer(external_writer);
    writer.join();
    return DeviceStatus::external_count;
}
