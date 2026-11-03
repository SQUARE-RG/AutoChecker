#define IF_DEBUG(x) if (x) { } } // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-1-2]

int main() {
    int debug = 1;
    {
        IF_DEBUG(debug)
        debug = 0;
        return debug;
    }
