#include <iostream>

class Document {
public:
    Document() : docid(0) {}
    explicit Document(int value) : docid(value) {}
    int docid;
};

class Book : public Document {
public:
    Book(int value);
    int bookid;
};

Book::Book(int value) : bookid(value)
// CHECK-MESSAGES: :[[@LINE-1]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-2-2-5]
{
}

int main() {
    Book mybook(2);
    std::cout << mybook.bookid << '\n';
    return 0;
}
