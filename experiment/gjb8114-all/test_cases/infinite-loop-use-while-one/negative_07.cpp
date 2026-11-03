#include <cstdint>

struct Sequence {
    static int run() {
        int sum = 0;
        for (int i = 0; ; ++i) // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-9-4]
        {
            sum += i;
            if (i == 2) {
                break;
            }
        }
        return sum;
    }
};

int main() {
    return Sequence::run() == 3 ? 0 : 1;
}
