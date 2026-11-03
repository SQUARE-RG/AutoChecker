typedef unsigned int UINT;

class Flags {
public:
    unsigned int enabled : 1;  // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-1-1]
    UINT visible : 1;
};
