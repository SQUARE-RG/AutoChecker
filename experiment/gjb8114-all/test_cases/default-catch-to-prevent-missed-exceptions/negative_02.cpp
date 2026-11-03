#include <exception>
#include <stdexcept>

int main() {
    try {
        throw 42;
    } catch (const std::exception&) {
        return 1;
    } catch (int) { // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-2-8-1]
        return 2;
    }
    return 0;
}
