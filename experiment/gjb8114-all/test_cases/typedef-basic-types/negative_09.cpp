typedef int SINT;

class Widget {
private:
    SINT value_ = 0;
public:
    int getValue() const { return value_; }  // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-1-1]
};
