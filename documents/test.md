# 소프트웨어 개발 모범 사례

소프트웨어 개발에서 고품질의 코드를 작성하고 유지보수하는 것은 프로젝트의 성공과 직결되는 매우 중요한 과제입니다. 이 문서는 견고하고 확장 가능하며 유지보수가 용이한 소프트웨어를 구축하는 데 도움이 되는 핵심적인 모범 사례들을 포괄적으로 소개합니다. 이 원칙들은 특정 언어나 프레임워크에 국한되지 않으며, 모든 소프트웨어 엔지니어가 숙지해야 할 기본적인 지침을 제공합니다.

---

## 목차

1.  SOLID 원칙: 견고한 객체 지향 설계
2.  코드 품질과 가독성
3.  버전 관리 시스템(VCS) 활용
4.  테스팅 전략
5.  코드 리뷰 문화
6.  CI/CD: 지속적인 통합과 배포
7.  보안 코딩
8.  문서화
9.  애자일 개발 방법론

---

## 1. SOLID 원칙: 견고한 객체 지향 설계

SOLID는 로버트 C. 마틴(Robert C. Martin)이 제시한 객체 지향 프로그래밍 및 설계의 다섯 가지 기본 원칙입니다. 이 원칙들을 따르면 시간이 지나도 유지보수하고 확장하기 쉬운 시스템을 만들 수 있습니다.

### 1.1. 단일 책임 원칙 (Single Responsibility Principle - SRP)

> "클래스는 단 하나의 변경 이유만을 가져야 한다."

클래스는 하나의 기능이나 책임만 가져야 합니다. 여러 책임을 가진 클래스는 변경이 필요할 때 예상치 못한 부작용을 일으킬 수 있습니다.

**나쁜 예:**
```java
// 보고서 생성과 데이터베이스 저장을 모두 처리하는 클래스
class Report {
    public void generateReport(String data) {
        System.out.println("Generating report with data: " + data);
        // 보고서 생성 로직...
    }

    public void saveToDatabase(String report) {
        System.out.println("Saving report to database...");
        // 데이터베이스 저장 로직...
    }
}
```

**좋은 예:**
```java
// 책임을 분리한 클래스들
class ReportGenerator {
    public String generate(String data) {
        System.out.println("Generating report with data: " + data);
        // 보고서 생성 로직...
        return "Generated Report";
    }
}

class ReportRepository {
    public void save(String report) {
        System.out.println("Saving report to database...");
        // 데이터베이스 저장 로직...
    }
}
```

### 1.2. 개방-폐쇄 원칙 (Open/Closed Principle - OCP)

> "소프트웨어 개체(클래스, 모듈, 함수 등)는 확장에 대해 열려 있어야 하고, 수정에 대해서는 닫혀 있어야 한다."

기존 코드를 변경하지 않고도 기능을 추가할 수 있어야 합니다. 이는 주로 추상화와 다형성을 통해 달성됩니다.

**나쁜 예:**
```python
# 새로운 도형을 추가할 때마다 AreaCalculator 클래스를 수정해야 함
class Rectangle:
    def __init__(self, width, height):
        self.width = width
        self.height = height

class Circle:
    def __init__(self, radius):
        self.radius = radius

class AreaCalculator:
    def calculate_area(self, shape):
        if isinstance(shape, Rectangle):
            return shape.width * shape.height
        elif isinstance(shape, Circle):
            return 3.14 * shape.radius ** 2
        # 새로운 도형이 추가될 때마다 이 부분을 수정해야 함
```

**좋은 예:**
```python
from abc import ABC, abstractmethod

# 추상 базовый 클래스를 사용하여 확장에는 열려있도록 설계
class Shape(ABC):
    @abstractmethod
    def area(self):
        pass

class Rectangle(Shape):
    def __init__(self, width, height):
        self.width = width
        self.height = height

    def area(self):
        return self.width * self.height

class Circle(Shape):
    def __init__(self, radius):
        self.radius = radius

    def area(self):
        return 3.14 * self.radius ** 2

# AreaCalculator는 Shape의 구체적인 타입을 알 필요가 없음
class AreaCalculator:
    def calculate_area(self, shape: Shape):
        return shape.area()

# 새로운 Triangle 클래스를 추가해도 AreaCalculator는 수정할 필요가 없음
class Triangle(Shape):
    def __init__(self, base, height):
        self.base = base
        self.height = height
    
    def area(self):
        return 0.5 * self.base * self.height
```

### 1.3. 리스코프 치환 원칙 (Liskov Substitution Principle - LSP)

> "서브타입은 언제나 기반 타입으로 교체될 수 있어야 한다."

자식 클래스는 부모 클래스의 역할을 온전히 수행할 수 있어야 합니다. 즉, 자식 클래스가 부모 클래스의 메서드를 오버라이드할 때, 부모 클래스의 의도와 다르게 동작해서는 안 됩니다.

**나쁜 예:**
```python
# Rectangle의 동작을 Square가 제대로 치환하지 못하는 경우
class Rectangle:
    def __init__(self, width, height):
        self.width = width
        self.height = height

    def set_width(self, width):
        self.width = width

    def set_height(self, height):
        self.height = height

    def get_area(self):
        return self.width * self.height

class Square(Rectangle):
    def __init__(self, size):
        super().__init__(size, size)

    def set_width(self, width):
        self.width = width
        self.height = width # 정사각형의 속성을 유지하기 위해 높이도 변경

    def set_height(self, height):
        self.width = height
        self.height = height # 너비도 변경

def test_rectangle_area(rect: Rectangle):
    rect.set_width(5)
    rect.set_height(4)
    # 사용자는 너비 5, 높이 4이므로 넓이가 20일 것으로 기대
    assert rect.get_area() == 20

# test_rectangle_area(Square(1))를 호출하면 Square의 set_width/set_height 동작으로 인해 AssertionError 발생
```

### 1.4. 인터페이스 분리 원칙 (Interface Segregation Principle - ISP)

> "클라이언트는 자신이 사용하지 않는 메서드에 의존하도록 강요되어서는 안 된다."

하나의 거대한 인터페이스보다는, 특정 클라이언트를 위한 여러 개의 작은 인터페이스로 분리하는 것이 좋습니다.

**나쁜 예:**
```java
// 모든 기능을 포함하는 거대한 인터페이스
interface Worker {
    void work();
    void eat();
    void sleep();
}

class HumanWorker implements Worker {
    public void work() { /* ... */ }
    public void eat() { /* ... */ }
    public void sleep() { /* ... */ }
}

class RobotWorker implements Worker {
    public void work() { /* ... */ }
    public void eat() { 
        // 로봇은 먹지 않으므로, 이 메서드는 불필요하거나 예외를 던져야 함
        throw new UnsupportedOperationException("Robot cannot eat");
    }
    public void sleep() {
        // 로봇은 잠을 자지 않음
        throw new UnsupportedOperationException("Robot cannot sleep");
    }
}
```

**좋은 예:**
```java
// 역할을 기준으로 인터페이스 분리
interface Workable {
    void work();
}

interface Feedable {
    void eat();
}

interface Restable {
    void sleep();
}

class HumanWorker implements Workable, Feedable, Restable {
    public void work() { /* ... */ }
    public void eat() { /* ... */ }
    public void sleep() { /* ... */ }
}

class RobotWorker implements Workable {
    public void work() { /* ... */ }
    // 필요 없는 eat(), sleep() 메서드를 구현할 필요가 없음
}
```

### 1.5. 의존관계 역전 원칙 (Dependency Inversion Principle - DIP)

> "상위 수준 모듈은 하위 수준 모듈에 의존해서는 안 된다. 둘 모두 추상화에 의존해야 한다."
> "추상화는 구체적인 사항에 의존해서는 안 된다. 구체적인 사항이 추상화에 의존해야 한다."

고수준 모듈이 저수준 모듈의 구체적인 구현에 직접 의존하는 대신, 둘 다 추상화(인터페이스 등)에 의존해야 합니다. 이는 의존성 주입(Dependency Injection)을 통해 달성할 수 있습니다.

**나쁜 예:**
```python
# Notification 클래스가 EmailSender 구체 클래스에 직접 의존
class EmailSender:
    def send(self, message):
        print(f"Sending email: {message}")

class Notification:
    def __init__(self):
        self.sender = EmailSender() # 구체적인 구현에 의존

    def send_notification(self, message):
        self.sender.send(message)
```

**좋은 예:**
```python
from abc import ABC, abstractmethod

# 추상화(인터페이스) 정의
class MessageSender(ABC):
    @abstractmethod
    def send(self, message):
        pass

# 구체적인 구현 클래스
class EmailSender(MessageSender):
    def send(self, message):
        print(f"Sending email: {message}")

class SmsSender(MessageSender):
    def send(self, message):
        print(f"Sending SMS: {message}")

# Notification 클래스는 추상화에 의존
class Notification:
    def __init__(self, sender: MessageSender): # 외부에서 의존성 주입
        self.sender = sender

    def send_notification(self, message):
        self.sender.send(message)

# 사용 시점에서 구체적인 구현을 주입
email_notification = Notification(EmailSender())
sms_notification = Notification(SmsSender())
```

---

## 2. 코드 품질과 가독성

깨끗하고 읽기 쉬운 코드는 협업과 유지보수를 용이하게 하며, 버그 발생 가능성을 줄입니다.

### 2.1. 의미 있는 이름 짓기

변수, 함수, 클래스의 이름은 그 역할과 의도를 명확하게 나타내야 합니다. 모호하거나 축약된 이름은 피하는 것이 좋습니다.

*   **의도를 드러내는 이름**: `d` 보다는 `elapsed_time_in_days`
*   **맥락이 분명한 이름**: `state` 보다는 `address_state`
*   **일관성 있는 이름**: `get_user`, `fetch_customer` 보다는 `get_user`, `get_customer`

**나쁜 예:**
```python
# 변수명이 너무 일반적이고 축약됨
data = get_data()
for i in data:
    # ...
```

**좋은 예:**
```python
# 역할이 명확히 드러나는 변수명
customer_list = fetch_customers()
for customer in customer_list:
    # ...
```

### 2.2. DRY (Don't Repeat Yourself) 원칙

> "모든 지식은 시스템 내에서 단 한번만, 모호하지 않고, 권위 있게 표현되어야 한다."

중복된 코드는 유지보수를 어렵게 만듭니다. 동일한 로직이 여러 곳에 반복된다면, 함수나 클래스로 추출하여 재사용해야 합니다.

**나쁜 예:**
```javascript
function processUser(user) {
    // 유효성 검사 로직
    if (!user.name || user.name.length === 0) {
        console.error("Invalid user name");
        return;
    }
    // ...
}

function processOrder(order) {
    // 유효성 검사 로직 (중복)
    if (!order.user.name || order.user.name.length === 0) {
        console.error("Invalid user name in order");
        return;
    }
    // ...
}
```

**좋은 예:**
```javascript
function isUserNameValid(name) {
    return name && name.length > 0;
}

function processUser(user) {
    if (!isUserNameValid(user.name)) {
        console.error("Invalid user name");
        return;
    }
    // ...
}

function processOrder(order) {
    if (!isUserNameValid(order.user.name)) {
        console.error("Invalid user name in order");
        return;
    }
    // ...
}
```

### 2.3. KISS (Keep It Simple, Stupid) 원칙

불필요하게 복잡한 설계나 코드는 피해야 합니다. 대부분의 문제는 간단한 해결책으로 풀 수 있습니다. 복잡성은 버그의 원인이 되고 이해하기 어렵게 만듭니다.

### 2.4. YAGNI (You Ain't Gonna Need It) 원칙

지금 당장 필요하지 않은 기능은 구현하지 마세요. 미래를 예측하여 미리 기능을 만드는 것은 종종 불필요한 복잡성을 추가하고 낭비로 이어질 수 있습니다.

### 2.5. 함수와 메서드 설계

*   **작게 만들기**: 함수는 한 가지 일만 해야 하며, 가급적 20줄을 넘지 않도록 노력합니다.
*   **단일 책임**: 함수는 이름에 걸맞은 한 가지 작업만 수행해야 합니다.
*   **적은 인자 수**: 함수의 인자는 3개 이하가 이상적입니다. 인자가 많아지면 객체로 묶는 것을 고려합니다.

### 2.6. 주석과 문서화

*   **코드로 의도를 표현**: 가장 좋은 주석은 주석이 필요 없는 코드입니다. 변수명과 함수명으로 의도를 명확히 표현하세요.
*   **'왜'를 설명**: 코드가 '무엇을' 하는지는 코드를 보면 알 수 있습니다. 주석은 '왜' 그렇게 작성했는지, 비즈니스 로직이나 특정 결정의 배경을 설명하는 데 사용해야 합니다.
*   **오해의 소지가 있는 코드 설명**: 복잡한 알고리즘이나 정규 표현식 등 한눈에 파악하기 어려운 코드는 주석으로 설명합니다.

### 2.7. 일관된 코드 스타일과 포매팅

팀 전체가 일관된 코드 스타일을 따르면 가독성이 향상되고 코드 리뷰가 수월해집니다.

*   **Linter 사용**: ESLint(JavaScript), Pylint(Python), Checkstyle(Java) 등과 같은 린팅 도구를 사용하여 코드 스타일과 잠재적인 오류를 검사합니다.
*   **Formatter 사용**: Prettier, Black(Python), ktlint(Kotlin) 등과 같은 코드 포매터를 사용하여 자동으로 코드 스타일을 통일합니다.

---

## 3. 버전 관리 시스템(VCS) 활용

Git과 같은 버전 관리 시스템을 사용하는 것은 현대 소프트웨어 개발의 필수 요소입니다.

### 3.1. 버전 관리의 중요성

*   **변경 이력 추적**: 코드의 모든 변경 사항을 기록하고 특정 시점으로 되돌아갈 수 있습니다.
*   **협업**: 여러 개발자가 동시에 효율적으로 작업할 수 있도록 돕습니다.
*   **브랜치 전략**: `feature`, `develop`, `main` 등과 같은 브랜치를 활용하여 체계적으로 개발을 관리합니다.
*   **코드 백업**: 원격 저장소(GitHub, GitLab 등)를 통해 코드를 안전하게 백업합니다.

### 3.2. 좋은 커밋 메시지 작성법

좋은 커밋 메시지는 코드 변경의 맥락을 이해하는 데 매우 중요합니다.

*   **제목과 본문 분리**: 첫 줄에 변경 내용을 요약한 제목을 작성하고, 한 줄을 비운 뒤 본문에 상세한 설명을 작성합니다.
*   **제목은 50자 이내로**: 제목은 간결하게 작성합니다.
*   **어떻게(How) 보다는 무엇(What)과 왜(Why)를 설명**: 코드 변경 자체보다는, 무엇을 변경했고 왜 변경했는지에 초점을 맞춥니다.
*   **명령문으로 작성**: "Fixed bug" 보다는 "Fix: 로그인 시 발생하는 버그 수정" 과 같이 명령문 형태로 작성합니다.

**좋은 커밋 메시지 예시:**
```
feat: 사용자 프로필 이미지 업로드 기능 추가

사용자가 자신의 프로필 이미지를 업로드하고 변경할 수 있는 기능을 추가합니다.

- 이미지 업로드를 위한 API 엔드포인트 (/api/users/profile-image)를 구현했습니다.
- 업로드된 이미지는 S3 버킷에 저장됩니다.
- 이미지 크기 및 형식 유효성 검사를 추가하여 안정성을 높였습니다.

Closes #123
```

### 3.3. 브랜치 전략

팀의 규모와 프로젝트의 특성에 맞는 브랜치 전략을 사용하는 것이 중요합니다.

*   **GitFlow**: `main`, `develop`, `feature`, `release`, `hotfix` 등 다양한 브랜치를 사용하여 기능 개발, 배포, 긴급 수정을 체계적으로 관리하는 전략입니다. 규모가 크고 정기적인 릴리즈가 있는 프로젝트에 적합합니다.
*   **GitHub Flow**: `main` 브랜치와 `feature` 브랜치만을 사용하는 간단한 전략입니다. `main` 브랜치는 항상 배포 가능한 상태로 유지되며, 모든 작업은 `feature` 브랜치에서 진행된 후 Pull Request를 통해 `main`으로 병합됩니다. CI/CD가 잘 구축된 프로젝트에 적합합니다.
*   **Trunk-Based Development**: 모든 개발자가 `main` (trunk) 브랜치에 직접 작업하는 방식입니다. 작은 단위의 커밋을 자주 푸시하며, 기능 플래그(Feature Flag)를 사용하여 미완성된 기능이 사용자에게 노출되지 않도록 제어합니다. 고도로 숙련된 팀과 강력한 자동화 테스트가 필수적입니다.

---

## 4. 테스팅 전략

버그를 조기에 발견하고 코드의 안정성을 보장하기 위해 테스트 코드를 작성하는 습관이 중요합니다. 테스트는 리팩토링과 기능 추가에 대한 자신감을 줍니다.

### 4.1. 테스트 피라미드

테스트 피라미드는 효율적인 테스트 전략을 수립하기 위한 모델입니다.

| 테스트 종류 | 목적 | 속도/비용 | 예시 (Jest) |
|---|---|---|---|
| **단위 테스트 (Unit Test)** | 개별 함수나 컴포넌트의 기능을 검증합니다. | 빠름 / 저렴 | `expect(sum(1, 2)).toBe(3);` |
| **통합 테스트 (Integration Test)** | 여러 컴포넌트가 함께 잘 동작하는지 확인합니다. | 보통 / 중간 | API 호출 후 DB 상태 검증 |
| **E2E 테스트 (End-to-End Test)** | 실제 사용자 시나리오를 시뮬레이션하여 전체 시스템을 검증합니다. | 느림 / 비쌈 | 로그인 -> 상품 구매 -> 로그아웃 |

피라미드의 아래쪽으로 갈수록 테스트의 양이 많아지고, 위로 갈수록 양이 적어져야 합니다.

### 4.2. 테스트 주도 개발 (Test-Driven Development - TDD)

TDD는 실제 코드를 작성하기 전에 실패하는 테스트 케이스를 먼저 작성하는 개발 방법론입니다.

1.  **Red**: 실패하는 테스트 코드를 작성합니다.
2.  **Green**: 테스트를 통과하는 최소한의 코드를 작성합니다.
3.  **Refactor**: 코드의 중복을 제거하고 구조를 개선합니다.

TDD는 더 견고하고 요구사항에 충실한 설계를 유도합니다.

### 4.3. 테스트 코드 예시 (Python - pytest)

```python
# calculator.py
def add(a, b):
    if not isinstance(a, (int, float)) or not isinstance(b, (int, float)):
        raise TypeError("Inputs must be numeric")
    return a + b

# test_calculator.py
import pytest
from .calculator import add

def test_add_positive_numbers():
    """두 양수를 더하는 경우"""
    assert add(2, 3) == 5

def test_add_negative_numbers():
    """두 음수를 더하는 경우"""
    assert add(-1, -5) == -6

def test_add_mixed_numbers():
    """양수와 음수를 더하는 경우"""
    assert add(10, -3) == 7

def test_add_with_non_numeric_input_raises_type_error():
    """숫자가 아닌 입력에 대해 TypeError를 발생시키는지 테스트"""
    with pytest.raises(TypeError):
        add("2", 3)

    with pytest.raises(TypeError):
        add(2, "3")
```

---

## 5. 코드 리뷰 문화

코드 리뷰는 코드 품질을 향상시키고, 지식을 공유하며, 팀원 간의 유대감을 형성하는 중요한 과정입니다.

### 5.1. 리뷰어(Reviewer)의 자세

*   **긍정적이고 건설적인 피드백**: 비난이 아닌 제안의 형태로 의견을 제시합니다. ("이 부분은 ~게 바꾸면 더 좋을 것 같아요.")
*   **원칙에 기반한 리뷰**: 개인적인 스타일 선호보다는, 팀에서 합의된 코딩 컨벤션이나 설계 원칙에 따라 리뷰합니다.
*   **칭찬하기**: 좋은 코드나 아이디어에 대해서는 적극적으로 칭찬하여 동기를 부여합니다.
*   **의도를 파악하기**: 코드가 이해되지 않으면 질문을 통해 작성자의 의도를 먼저 파악합니다.

### 5.2. 작성자(Author)의 자세

*   **작은 단위로 리뷰 요청**: 리뷰어가 집중할 수 있도록 작고 논리적인 단위로 Pull Request(PR)를 생성합니다.
*   **셀프 리뷰**: PR을 생성하기 전에 자신의 코드를 먼저 리뷰하며 오타나 명백한 오류를 수정합니다.
*   **충분한 설명 제공**: PR 설명에 변경 사항의 배경, 목적, 주요 변경 내용을 상세히 작성하여 리뷰어가 맥락을 이해하도록 돕습니다.
*   **피드백에 열린 자세**: 리뷰는 코드에 대한 비판이지 개인에 대한 비판이 아님을 인지하고, 건설적인 피드백을 겸허히 수용합니다.

---

## 6. CI/CD: 지속적인 통합과 배포

### 6.1. 지속적인 통합 (Continuous Integration - CI)

CI는 모든 개발자가 작업한 내용을 주기적으로(보통 하루에 여러 번) 중앙 저장소에 병합하는 프로세스입니다. 각 병합 시마다 빌드와 자동화된 테스트가 실행되어 통합 오류를 조기에 발견할 수 있습니다.

**CI 파이프라인 예시 (GitHub Actions):**
```yaml
name: CI Pipeline

on: [push, pull_request]

jobs:
  build-and-test:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt

      - name: Run linter
        run: |
          pip install flake8
          flake8 .

      - name: Run tests
        run: |
          pip install pytest
          pytest
```

### 6.2. 지속적인 배포/전달 (Continuous Deployment/Delivery - CD)

*   **지속적인 전달(Delivery)**: CI 단계를 통과한 코드가 언제든지 배포될 수 있는 상태로 준비되는 것을 의미합니다. 실제 프로덕션 배포는 수동으로 트리거됩니다.
*   **지속적인 배포(Deployment)**: CI/CD 파이프라인의 모든 단계를 통과한 코드가 자동으로 프로덕션 환경에 배포되는 것을 의미합니다.

CD는 새로운 기능을 사용자에게 더 빠르고 안정적으로 제공할 수 있게 해줍니다.

---

## 7. 보안 코딩

애플리케이션의 잠재적인 보안 취약점을 예방하기 위해 개발 초기 단계부터 보안을 고려해야 합니다. (Shift-left security)

### 7.1. 입력값 검증

사용자로부터 들어오는 모든 입력값은 신뢰할 수 없다고 가정하고 항상 검증해야 합니다.

*   **SQL 인젝션 방지**: Prepared Statement(Parameter-ized Query)나 ORM을 사용하여 쿼리를 실행합니다.
*   **XSS (Cross-Site Scripting) 방지**: 사용자 입력을 출력할 때 적절한 이스케이프(escaping) 처리를 합니다.

### 7.2. 의존성 관리

사용하는 외부 라이브러리나 프레임워크의 보안 취약점을 정기적으로 검사하고 업데이트해야 합니다.

*   **도구 사용**: `npm audit`, `pip-audit`, GitHub의 Dependabot과 같은 도구를 사용하여 취약점을 자동으로 탐지하고 알림을 받습니다.

### 7.3. 최소 권한 원칙

시스템의 각 구성요소는 자신의 작업을 수행하는 데 필요한 최소한의 권한만 가져야 합니다. 예를 들어, 읽기 전용 작업만 필요한 데이터베이스 사용자는 `SELECT` 권한만 가져야 합니다.

### 7.4. 비밀 정보 관리

API 키, 데이터베이스 비밀번호 등과 같은 민감한 정보는 코드에 하드코딩해서는 안 됩니다.

*   **환경 변수 사용**: 환경 변수를 통해 민감한 정보를 주입합니다.
*   **Secret Management 도구 사용**: AWS Secrets Manager, HashiCorp Vault, Google Secret Manager와 같은 전문 도구를 사용하여 비밀 정보를 안전하게 관리합니다.

---

## 8. 문서화

좋은 문서는 프로젝트의 유지보수성과 확장성을 높이고, 새로운 팀원이 빠르게 적응할 수 있도록 돕습니다.

### 8.1. 문서화 대상

*   **README.md**: 프로젝트의 개요, 설치 방법, 실행 방법, 기본 사용법 등을 포함하는 프로젝트의 첫인상입니다.
*   **API 문서**: 각 엔드포인트의 URL, HTTP 메서드, 요청/응답 형식, 파라미터, 인증 방법 등을 명확하게 기술합니다. (Swagger/OpenAPI 사용 권장)
*   **아키텍처 문서**: 시스템의 전체적인 구조, 주요 컴포넌트 간의 관계, 데이터 흐름 등을 다이어그램과 함께 설명합니다.
*   **코드 주석**: 위에서 설명한 대로, '왜'에 초점을 맞춘 주석을 작성합니다.

### 8.2. 문서화 원칙

*   **독자를 고려**: 누가 이 문서를 읽을 것인지 생각하고 그에 맞는 수준으로 작성합니다.
*   **최신 상태 유지**: 코드가 변경될 때 관련 문서도 함께 업데이트하는 습관을 들입니다. 오래된 문서는 없는 것보다 해로울 수 있습니다.
*   **간결하고 명확하게**: 불필요한 내용은 피하고, 핵심 정보를 쉽게 이해할 수 있도록 작성합니다.

---

## 9. 애자일 개발 방법론

애자일은 계획을 따르기보다 변화에 유연하게 대응하며, 짧은 주기의 반복적인 개발을 통해 소프트웨어를 점진적으로 완성해나가는 방법론입니다.

### 9.1. 스크럼 (Scrum)

스크럼은 애자일 개발을 위한 프레임워크 중 하나로, 다음과 같은 요소로 구성됩니다.

*   **스프린트(Sprint)**: 1~4주 단위의 짧은 개발 주기. 각 스프린트마다 실제 동작하는 제품의 일부를 개발합니다.
*   **제품 백로그(Product Backlog)**: 개발해야 할 모든 기능과 요구사항을 우선순위에 따라 정리한 목록입니다.
*   **스프린트 백로그(Sprint Backlog)**: 이번 스프린트에서 처리할 작업 목록입니다.
*   **일일 스크럼(Daily Scrum)**: 매일 진행되는 짧은 회의로, 어제 한 일, 오늘 할 일, 장애물을 공유합니다.

### 9.2. 칸반 (Kanban)

칸반은 작업 흐름을 시각화하고, 진행 중인 작업(Work in Progress - WIP)의 수를 제한하여 병목 현상을 관리하는 데 중점을 둔 방법론입니다. `To Do`, `In Progress`, `Done`과 같은 열로 구성된 칸반 보드를 사용하여 작업의 흐름을 한눈에 파악할 수 있습니다.

---

더 자세한 정보는 Google Engineering Practices 문서에서 확인하실 수 있습니다.

