struct Counter {
    int value;
    void run();
};

void Counter::run() {
    for (this->value = 0; this->value < 10; ++this->value) // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-9-1]
    {
    }
}

int main() {
    Counter counter;
    counter.run();
    return 0;
}
