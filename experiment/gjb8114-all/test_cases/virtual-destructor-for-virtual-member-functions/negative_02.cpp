#include <iostream>
#include <string>

struct Logger {
    ~Logger() = default;  // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-2-3-1]
    virtual void log(const std::string& message) = 0;
    virtual int verbosity() const = 0;
};

class ConsoleLogger : public Logger {
public:
    void log(const std::string& message) override
    {
        std::cout << message << '\n';
    }
    int verbosity() const override { return 1; }
};

int main()
{
    Logger* logger = new ConsoleLogger();
    logger->log("hello");
    delete logger;
    return 0;
}
