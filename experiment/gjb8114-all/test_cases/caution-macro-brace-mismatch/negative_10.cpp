#define BEGIN_ENUM(name) enum class name { // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-1-2]

BEGIN_ENUM(Color)
    Red,
    Green
};

int main()
{
    return static_cast<int>(Color::Green);
}
