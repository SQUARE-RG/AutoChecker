class LaunchController {
public:
    static int retryCount; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-13-1]
};

int LaunchController::retryCount = 0;

int main() {
    LaunchController::retryCount = 1;
    return LaunchController::retryCount;
}
