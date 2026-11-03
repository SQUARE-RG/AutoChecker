struct Counter {
    int update(int delta) { // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-7-2]
        return count_;
    }

    int count_ = 0;
};
