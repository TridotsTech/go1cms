"function" != typeof Object.create && (Object.create = function(b) {
        function a() {}
        return a.prototype = b, new a
    }),
    function(a, b, c) {
        var d = {
            init: function(b, c) {
                this.$elem = a(c), this.options = a.extend({}, a.fn.owlCarousel.options, this.$elem.data(), b), this.userOptions = b, this.loadContent()
            },
            loadContent: function() {
                var c, b = this;
                "function" == typeof b.options.beforeInit && b.options.beforeInit.apply(this, [b.$elem]), "string" == typeof b.options.jsonPath ? (c = b.options.jsonPath, a.getJSON(c, function(a) {
                    var c, d = "";
                    if ("function" == typeof b.options.jsonSuccess) b.options.jsonSuccess.apply(this, [a]);
                    else {
                        for (c in a.owl) a.owl.hasOwnProperty(c) && (d += a.owl[c].item);
                        b.$elem.html(d)
                    }
                    b.logIn()
                })) : b.logIn()
            },
            logIn: function() {
                this.$elem.data("owl-originalStyles", this.$elem.attr("style")), this.$elem.data("owl-originalClasses", this.$elem.attr("class")), this.$elem.css({
                    opacity: 0
                }), this.orignalItems = this.options.items, this.checkBrowser(), this.wrapperWidth = 0, this.checkVisible = null, this.setVars()
            },
            setVars: function() {
                if (0 === this.$elem.children().length) return !1;
                this.baseClass(), this.eventTypes(), this.$userItems = this.$elem.children(), this.itemsAmount = this.$userItems.length, this.wrapItems(), this.$owlItems = this.$elem.find(".owl-item"), this.$owlWrapper = this.$elem.find(".owl-wrapper"), this.playDirection = "next", this.prevItem = 0, this.prevArr = [0], this.currentItem = 0, this.customEvents(), this.onStartup()
            },
            onStartup: function() {
                this.updateItems(), this.calculateAll(), this.buildControls(), this.updateControls(), this.response(), this.moveEvents(), this.stopOnHover(), this.owlStatus(), !1 !== this.options.transitionStyle && this.transitionTypes(this.options.transitionStyle), !0 === this.options.autoPlay && (this.options.autoPlay = 5e3), this.play(), this.$elem.find(".owl-wrapper").css("display", "block"), this.$elem.is(":visible") ? this.$elem.css("opacity", 1) : this.watchVisibility(), this.onstartup = !1, this.eachMoveUpdate(), "function" == typeof this.options.afterInit && this.options.afterInit.apply(this, [this.$elem])
            },
            eachMoveUpdate: function() {
                !0 === this.options.lazyLoad && this.lazyLoad(), !0 === this.options.autoHeight && this.autoHeight(), this.onVisibleItems(), "function" == typeof this.options.afterAction && this.options.afterAction.apply(this, [this.$elem])
            },
            updateVars: function() {
                "function" == typeof this.options.beforeUpdate && this.options.beforeUpdate.apply(this, [this.$elem]), this.watchVisibility(), this.updateItems(), this.calculateAll(), this.updatePosition(), this.updateControls(), this.eachMoveUpdate(), "function" == typeof this.options.afterUpdate && this.options.afterUpdate.apply(this, [this.$elem])
            },
            reload: function() {
                var a = this;
                b.setTimeout(function() {
                    a.updateVars()
                }, 0)
            },
            watchVisibility: function() {
                var a = this;
                if (!1 !== a.$elem.is(":visible")) return !1;
                a.$elem.css({
                    opacity: 0
                }), b.clearInterval(a.autoPlayInterval), b.clearInterval(a.checkVisible), a.checkVisible = b.setInterval(function() {
                    a.$elem.is(":visible") && (a.reload(), a.$elem.animate({
                        opacity: 1
                    }, 200), b.clearInterval(a.checkVisible))
                }, 500)
            },
            wrapItems: function() {
                this.$userItems.wrapAll('<div class="owl-wrapper">').wrap('<div class="owl-item"></div>'), this.$elem.find(".owl-wrapper").wrap('<div class="owl-wrapper-outer">'), this.wrapperOuter = this.$elem.find(".owl-wrapper-outer"), this.$elem.css("display", "block")
            },
            baseClass: function() {
                var a = this.$elem.hasClass(this.options.baseClass),
                    b = this.$elem.hasClass(this.options.theme);
                a || this.$elem.addClass(this.options.baseClass), b || this.$elem.addClass(this.options.theme)
            },
            updateItems: function() {
                var b, c;
                if (!1 === this.options.responsive) return !1;
                if (!0 === this.options.singleItem) return this.options.items = this.orignalItems = 1, this.options.itemsCustom = !1, this.options.itemsDesktop = !1, this.options.itemsDesktopSmall = !1, this.options.itemsTablet = !1, this.options.itemsTabletSmall = !1, this.options.itemsMobile = !1, !1;
                if ((b = a(this.options.responsiveBaseWidth).width()) > (this.options.itemsDesktop[0] || this.orignalItems) && (this.options.items = this.orignalItems), !1 !== this.options.itemsCustom)
                    for (this.options.itemsCustom.sort(function(a, b) {
                            return a[0] - b[0]
                        }), c = 0; c < this.options.itemsCustom.length; c += 1) this.options.itemsCustom[c][0] <= b && (this.options.items = this.options.itemsCustom[c][1]);
                else b <= this.options.itemsDesktop[0] && !1 !== this.options.itemsDesktop && (this.options.items = this.options.itemsDesktop[1]), b <= this.options.itemsDesktopSmall[0] && !1 !== this.options.itemsDesktopSmall && (this.options.items = this.options.itemsDesktopSmall[1]), b <= this.options.itemsTablet[0] && !1 !== this.options.itemsTablet && (this.options.items = this.options.itemsTablet[1]), b <= this.options.itemsTabletSmall[0] && !1 !== this.options.itemsTabletSmall && (this.options.items = this.options.itemsTabletSmall[1]), b <= this.options.itemsMobile[0] && !1 !== this.options.itemsMobile && (this.options.items = this.options.itemsMobile[1]);
                this.options.items > this.itemsAmount && !0 === this.options.itemsScaleUp && (this.options.items = this.itemsAmount)
            },
            response: function() {
                var e, d, c = this;
                if (!0 !== c.options.responsive) return !1;
                d = a(b).width(), c.resizer = function() {
                    a(b).width() !== d && (!1 !== c.options.autoPlay && b.clearInterval(c.autoPlayInterval), b.clearTimeout(e), e = b.setTimeout(function() {
                        d = a(b).width(), c.updateVars()
                    }, c.options.responsiveRefreshRate))
                }, a(b).resize(c.resizer)
            },
            updatePosition: function() {
                this.jumpTo(this.currentItem), !1 !== this.options.autoPlay && this.checkAp()
            },
            appendItemsSizes: function() {
                var b = this,
                    c = 0,
                    d = b.itemsAmount - b.options.items;
                b.$owlItems.each(function(e) {
                    var f = a(this);
                    f.css({
                        width: b.itemWidth
                    }).data("owl-item", Number(e)), e % b.options.items != 0 && e !== d || e > d || (c += 1), f.data("owl-roundPages", c)
                })
            },
            appendWrapperSizes: function() {
                var a = this.$owlItems.length * this.itemWidth;
                this.$owlWrapper.css({
                    width: 2 * a,
                    left: 0
                }), this.appendItemsSizes()
            },
            calculateAll: function() {
                this.calculateWidth(), this.appendWrapperSizes(), this.loops(), this.max()
            },
            calculateWidth: function() {
                this.itemWidth = Math.round(this.$elem.width() / this.options.items)
            },
            max: function() {
                var a = -1 * (this.itemsAmount * this.itemWidth - this.options.items * this.itemWidth);
                return this.options.items > this.itemsAmount ? (this.maximumItem = 0, a = 0, this.maximumPixels = 0) : (this.maximumItem = this.itemsAmount - this.options.items, this.maximumPixels = a), a
            },
            min: function() {
                return 0
            },
            loops: function() {
                var b, d, c = 0,
                    e = 0;
                for (this.positionsInArray = [0], this.pagesInArray = [], b = 0; b < this.itemsAmount; b += 1) e += this.itemWidth, this.positionsInArray.push(-e), !0 === this.options.scrollPerPage && (d = a(this.$owlItems[b]).data("owl-roundPages")) !== c && (this.pagesInArray[c] = this.positionsInArray[b], c = d)
            },
            buildControls: function() {
                !0 !== this.options.navigation && !0 !== this.options.pagination || (this.owlControls = a('<div class="owl-controls"/>').toggleClass("clickable", !this.browser.isTouch).appendTo(this.$elem)), !0 === this.options.pagination && this.buildPagination(), !0 === this.options.navigation && this.buildButtons()
            },
            buildButtons: function() {
                var b = this,
                    c = a('<div class="owl-buttons"/>');
                b.owlControls.append(c), b.buttonPrev = a("<div/>", {
                    class: "owl-prev",
                    html: b.options.navigationText[0] || ""
                }), b.buttonNext = a("<div/>", {
                    class: "owl-next",
                    html: b.options.navigationText[1] || ""
                }), c.append(b.buttonPrev).append(b.buttonNext), c.on("touchstart.owlControls mousedown.owlControls", 'div[class^="owl"]', function(a) {
                    a.preventDefault()
                }), c.on("touchend.owlControls mouseup.owlControls", 'div[class^="owl"]', function(c) {
                    c.preventDefault(), a(this).hasClass("owl-next") ? b.next() : b.prev()
                })
            },
            buildPagination: function() {
                var b = this;
                b.paginationWrapper = a('<div class="owl-pagination"/>'), b.owlControls.append(b.paginationWrapper), b.paginationWrapper.on("touchend.owlControls mouseup.owlControls", ".owl-page", function(c) {
                    c.preventDefault(), Number(a(this).data("owl-page")) !== b.currentItem && b.goTo(Number(a(this).data("owl-page")), !0)
                })
            },
            updatePagination: function() {
                var d, e, f, b, c, g;
                if (!1 === this.options.pagination) return !1;
                for (this.paginationWrapper.html(""), d = 0, e = this.itemsAmount - this.itemsAmount % this.options.items, b = 0; b < this.itemsAmount; b += 1) b % this.options.items == 0 && (d += 1, e === b && (f = this.itemsAmount - this.options.items), c = a("<div/>", {
                    class: "owl-page"
                }), g = a("<span></span>", {
                    text: !0 === this.options.paginationNumbers ? d : "",
                    class: !0 === this.options.paginationNumbers ? "owl-numbers" : ""
                }), c.append(g), c.data("owl-page", e === b ? f : b), c.data("owl-roundPages", d), this.paginationWrapper.append(c));
                this.checkPagination()
            },
            checkPagination: function() {
                var b = this;
                if (!1 === b.options.pagination) return !1;
                b.paginationWrapper.find(".owl-page").each(function() {
                    a(this).data("owl-roundPages") === a(b.$owlItems[b.currentItem]).data("owl-roundPages") && (b.paginationWrapper.find(".owl-page").removeClass("active"), a(this).addClass("active"))
                })
            },
            checkNavigation: function() {
                if (!1 === this.options.navigation) return !1;
                !1 === this.options.rewindNav && (0 === this.currentItem && 0 === this.maximumItem ? (this.buttonPrev.addClass("disabled"), this.buttonNext.addClass("disabled")) : 0 === this.currentItem && 0 !== this.maximumItem ? (this.buttonPrev.addClass("disabled"), this.buttonNext.removeClass("disabled")) : this.currentItem === this.maximumItem ? (this.buttonPrev.removeClass("disabled"), this.buttonNext.addClass("disabled")) : 0 !== this.currentItem && this.currentItem !== this.maximumItem && (this.buttonPrev.removeClass("disabled"), this.buttonNext.removeClass("disabled")))
            },
            updateControls: function() {
                this.updatePagination(), this.checkNavigation(), this.owlControls && (this.options.items >= this.itemsAmount ? this.owlControls.hide() : this.owlControls.show())
            },
            destroyControls: function() {
                this.owlControls && this.owlControls.remove()
            },
            next: function(a) {
                if (this.isTransition) return !1;
                if (this.currentItem += parseInt(!0 === this.options.scrollPerPage ? this.options.items : 1), this.currentItem > this.maximumItem + (!0 === this.options.scrollPerPage ? this.options.items - 1 : 0)) {
                    if (!0 !== this.options.rewindNav) return this.currentItem = this.maximumItem, !1;
                    this.currentItem = 0, a = "rewind"
                }
                a = "rewind", this.goTo(this.currentItem, a)
            },
            prev: function(a) {
                if (this.isTransition) return !1;
                if (!0 === this.options.scrollPerPage && this.currentItem > 0 && this.currentItem < this.options.items ? this.currentItem = 0 : this.currentItem -= !0 === this.options.scrollPerPage ? this.options.items : 1, this.currentItem < 0) {
                    if (!0 !== this.options.rewindNav) return this.currentItem = 0, !1;
                    this.currentItem = this.maximumItem, a = "rewind"
                }
                a = "rewind", this.goTo(this.currentItem, a)
            },
            goTo: function(c, e, f) {
                var d, a = this;
                return !a.isTransition && ("function" == typeof a.options.beforeMove && a.options.beforeMove.apply(this, [a.$elem]), c >= a.maximumItem ? c = a.maximumItem : c <= 0 && (c = 0), a.currentItem = a.owl.currentItem = c, !1 !== a.options.transitionStyle && "drag" !== f && 1 === a.options.items && !0 === a.browser.support3d ? (a.swapSpeed(0), !0 === a.browser.support3d ? a.transition3d(a.positionsInArray[c]) : a.css2slide(a.positionsInArray[c], 1), a.afterGo(), a.singleItemTransition(), !1) : (d = a.positionsInArray[c], !0 === a.browser.support3d ? (a.isCss3Finish = !1, !0 === e ? (a.swapSpeed("paginationSpeed"), b.setTimeout(function() {
                    a.isCss3Finish = !0
                }, a.options.paginationSpeed)) : "rewind" === e ? (a.swapSpeed(a.options.rewindSpeed), b.setTimeout(function() {
                    a.isCss3Finish = !0
                }, a.options.rewindSpeed)) : (a.swapSpeed("slideSpeed"), b.setTimeout(function() {
                    a.isCss3Finish = !0
                }, a.options.slideSpeed)), a.transition3d(d)) : !0 === e ? a.css2slide(d, a.options.paginationSpeed) : "rewind" === e ? a.css2slide(d, a.options.rewindSpeed) : a.css2slide(d, a.options.slideSpeed), void a.afterGo()))
            },
            jumpTo: function(a) {
                "function" == typeof this.options.beforeMove && this.options.beforeMove.apply(this, [this.$elem]), a >= this.maximumItem || -1 === a ? a = this.maximumItem : a <= 0 && (a = 0), this.swapSpeed(0), !0 === this.browser.support3d ? this.transition3d(this.positionsInArray[a]) : this.css2slide(this.positionsInArray[a], 1), this.currentItem = this.owl.currentItem = a, this.afterGo()
            },
            afterGo: function() {
                this.prevArr.push(this.currentItem), this.prevItem = this.owl.prevItem = this.prevArr[this.prevArr.length - 2], this.prevArr.shift(0), this.prevItem !== this.currentItem && (this.checkPagination(), this.checkNavigation(), this.eachMoveUpdate(), !1 !== this.options.autoPlay && this.checkAp()), "function" == typeof this.options.afterMove && this.prevItem !== this.currentItem && this.options.afterMove.apply(this, [this.$elem])
            },
            stop: function() {
                this.apStatus = "stop", b.clearInterval(this.autoPlayInterval)
            },
            checkAp: function() {
                "stop" !== this.apStatus && this.play()
            },
            play: function() {
                var a = this;
                if (a.apStatus = "play", !1 === a.options.autoPlay) return !1;
                b.clearInterval(a.autoPlayInterval), a.autoPlayInterval = b.setInterval(function() {
                    a.next(!0)
                }, a.options.autoPlay)
            },
            swapSpeed: function(a) {
                "slideSpeed" === a ? this.$owlWrapper.css(this.addCssSpeed(this.options.slideSpeed)) : "paginationSpeed" === a ? this.$owlWrapper.css(this.addCssSpeed(this.options.paginationSpeed)) : "string" != typeof a && this.$owlWrapper.css(this.addCssSpeed(a))
            },
            addCssSpeed: function(a) {
                return {
                    "-webkit-transition": "all " + a + "ms ease",
                    "-moz-transition": "all " + a + "ms ease",
                    "-o-transition": "all " + a + "ms ease",
                    transition: "all " + a + "ms ease"
                }
            },
            removeTransition: function() {
                return {
                    "-webkit-transition": "",
                    "-moz-transition": "",
                    "-o-transition": "",
                    transition: ""
                }
            },
            doTranslate: function(a) {
                return {
                    "-webkit-transform": "translate3d(" + a + "px, 0px, 0px)",
                    "-moz-transform": "translate3d(" + a + "px, 0px, 0px)",
                    "-o-transform": "translate3d(" + a + "px, 0px, 0px)",
                    "-ms-transform": "translate3d(" + a + "px, 0px, 0px)",
                    transform: "translate3d(" + a + "px, 0px,0px)"
                }
            },
            transition3d: function(a) {
                this.$owlWrapper.css(this.doTranslate(a))
            },
            css2move: function(a) {
                this.$owlWrapper.css({
                    left: a
                })
            },
            css2slide: function(b, c) {
                var a = this;
                a.isCssFinish = !1, a.$owlWrapper.stop(!0, !0).animate({
                    left: b
                }, {
                    duration: c || a.options.slideSpeed,
                    complete: function() {
                        a.isCssFinish = !0
                    }
                })
            },
            checkBrowser: function() {
                var d, e, f, g, a = "translate3d(0px, 0px, 0px)",
                    h = c.createElement("div");
                h.style.cssText = "  -moz-transform:" + a + "; -ms-transform:" + a + "; -o-transform:" + a + "; -webkit-transform:" + a + "; transform:" + a, d = /translate3d\(0px, 0px, 0px\)/g, f = null !== (e = h.style.cssText.match(d)) && 1 === e.length, g = "ontouchstart" in b || b.navigator.msMaxTouchPoints, this.browser = {
                    support3d: f,
                    isTouch: g
                }
            },
            moveEvents: function() {
                !1 === this.options.mouseDrag && !1 === this.options.touchDrag || (this.gestures(), this.disabledEvents())
            },
            eventTypes: function() {
                var a = ["s", "e", "x"];
                this.ev_types = {}, !0 === this.options.mouseDrag && !0 === this.options.touchDrag ? a = ["touchstart.owl mousedown.owl", "touchmove.owl mousemove.owl", "touchend.owl touchcancel.owl mouseup.owl"] : !1 === this.options.mouseDrag && !0 === this.options.touchDrag ? a = ["touchstart.owl", "touchmove.owl", "touchend.owl touchcancel.owl"] : !0 === this.options.mouseDrag && !1 === this.options.touchDrag && (a = ["mousedown.owl", "mousemove.owl", "mouseup.owl"]), this.ev_types.start = a[0], this.ev_types.move = a[1], this.ev_types.end = a[2]
            },
            disabledEvents: function() {
                this.$elem.on("dragstart.owl", function(a) {
                    a.preventDefault()
                }), this.$elem.on("mousedown.disableTextSelect", function(b) {
                    return a(b.target).is("input, textarea, select, option")
                })
            },
            gestures: function() {
                var d = this,
                    e = {
                        offsetX: 0,
                        offsetY: 0,
                        baseElWidth: 0,
                        relativePos: 0,
                        position: null,
                        minSwipe: null,
                        maxSwipe: null,
                        sliding: null,
                        dargging: null,
                        targetElement: null
                    };
                function f(a) {
                    if (void 0 !== a.touches) return {
                        x: a.touches[0].pageX,
                        y: a.touches[0].pageY
                    };
                    if (void 0 === a.touches) {
                        if (void 0 !== a.pageX) return {
                            x: a.pageX,
                            y: a.pageY
                        };
                        if (void 0 === a.pageX) return {
                            x: a.clientX,
                            y: a.clientY
                        }
                    }
                }
                function g(b) {
                    "on" === b ? (a(c).on(d.ev_types.move, h), a(c).on(d.ev_types.end, i)) : "off" === b && (a(c).off(d.ev_types.move), a(c).off(d.ev_types.end))
                }
                function h(h) {
                    var i, j, g = h.originalEvent || h || b.event;
                    d.newPosX = f(g).x - e.offsetX, d.newPosY = f(g).y - e.offsetY, d.newRelativeX = d.newPosX - e.relativePos, "function" == typeof d.options.startDragging && !0 !== e.dragging && 0 !== d.newRelativeX && (e.dragging = !0, d.options.startDragging.apply(d, [d.$elem])), (d.newRelativeX > 8 || d.newRelativeX < -8) && !0 === d.browser.isTouch && (void 0 !== g.preventDefault ? g.preventDefault() : g.returnValue = !1, e.sliding = !0), (d.newPosY > 10 || d.newPosY < -10) && !1 === e.sliding && a(c).off("touchmove.owl"), i = function() {
                        return d.newRelativeX / 5
                    }, j = function() {
                        return d.maximumPixels + d.newRelativeX / 5
                    }, d.newPosX = Math.max(Math.min(d.newPosX, i()), j()), !0 === d.browser.support3d ? d.transition3d(d.newPosX) : d.css2move(d.newPosX)
                }
                function i(f) {
                    var h, i, j, c = f.originalEvent || f || b.event;
                    c.target = c.target || c.srcElement, e.dragging = !1, !0 !== d.browser.isTouch && d.$owlWrapper.removeClass("grabbing"), d.newRelativeX < 0 ? d.dragDirection = d.owl.dragDirection = "left" : d.dragDirection = d.owl.dragDirection = "right", 0 !== d.newRelativeX && (h = d.getNewPosition(), d.goTo(h, !1, "drag"), e.targetElement === c.target && !0 !== d.browser.isTouch && (a(c.target).on("click.disable", function(b) {
                        b.stopImmediatePropagation(), b.stopPropagation(), b.preventDefault(), a(b.target).off("click.disable")
                    }), j = (i = a._data(c.target, "events").click).pop(), i.splice(0, 0, j))), g("off")
                }
                d.isCssFinish = !0, d.$elem.on(d.ev_types.start, ".owl-wrapper", function(i) {
                    var h, c = i.originalEvent || i || b.event;
                    if (3 === c.which) return !1;
                    if (!(d.itemsAmount <= d.options.items)) {
                        if (!1 === d.isCssFinish && !d.options.dragBeforeAnimFinish) return !1;
                        if (!1 === d.isCss3Finish && !d.options.dragBeforeAnimFinish) return !1;
                        !1 !== d.options.autoPlay && b.clearInterval(d.autoPlayInterval), !0 === d.browser.isTouch || d.$owlWrapper.hasClass("grabbing") || d.$owlWrapper.addClass("grabbing"), d.newPosX = 0, d.newRelativeX = 0, a(this).css(d.removeTransition()), h = a(this).position(), e.relativePos = h.left, e.offsetX = f(c).x - h.left, e.offsetY = f(c).y - h.top, g("on"), e.sliding = !1, e.targetElement = c.target || c.srcElement
                    }
                })
            },
            getNewPosition: function() {
                var a = this.closestItem();
                return a > this.maximumItem ? (this.currentItem = this.maximumItem, a = this.maximumItem) : this.newPosX >= 0 && (a = 0, this.currentItem = 0), a
            },
            closestItem: function() {
                var b = this,
                    c = !0 === b.options.scrollPerPage ? b.pagesInArray : b.positionsInArray,
                    e = b.newPosX,
                    d = null;
                return a.each(c, function(f, g) {
                    e - b.itemWidth / 20 > c[f + 1] && e - b.itemWidth / 20 < g && "left" === b.moveDirection() ? (d = g, !0 === b.options.scrollPerPage ? b.currentItem = a.inArray(d, b.positionsInArray) : b.currentItem = f) : e + b.itemWidth / 20 < g && e + b.itemWidth / 20 > (c[f + 1] || c[f] - b.itemWidth) && "right" === b.moveDirection() && (!0 === b.options.scrollPerPage ? (d = c[f + 1] || c[c.length - 1], b.currentItem = a.inArray(d, b.positionsInArray)) : (d = c[f + 1], b.currentItem = f + 1))
                }), b.currentItem
            },
            moveDirection: function() {
                var a;
                return this.newRelativeX < 0 ? (a = "right", this.playDirection = "next") : (a = "left", this.playDirection = "prev"), a
            },
            customEvents: function() {
                var a = this;
                a.$elem.on("owl.next", function() {
                    a.next()
                }), a.$elem.on("owl.prev", function() {
                    a.prev()
                }), a.$elem.on("owl.play", function(c, b) {
                    a.options.autoPlay = b, a.play(), a.hoverStatus = "play"
                }), a.$elem.on("owl.stop", function() {
                    a.stop(), a.hoverStatus = "stop"
                }), a.$elem.on("owl.goTo", function(c, b) {
                    a.goTo(b)
                }), a.$elem.on("owl.jumpTo", function(c, b) {
                    a.jumpTo(b)
                })
            },
            stopOnHover: function() {
                var a = this;
                !0 === a.options.stopOnHover && !0 !== a.browser.isTouch && !1 !== a.options.autoPlay && (a.$elem.on("mouseover", function() {
                    a.stop()
                }), a.$elem.on("mouseout", function() {
                    "stop" !== a.hoverStatus && a.play()
                }))
            },
            lazyLoad: function() {
                var c, b, e, d;
                if (!1 === this.options.lazyLoad) return !1;
                for (c = 0; c < this.itemsAmount; c += 1) "loaded" !== (b = a(this.$owlItems[c])).data("owl-loaded") && (e = b.data("owl-item"), "string" == typeof(d = b.find(".lazyOwl")).data("src") ? (void 0 === b.data("owl-loaded") && (d.hide(), b.addClass("loading").data("owl-loaded", "checked")), (!0 !== this.options.lazyFollow || e >= this.currentItem) && e < this.currentItem + this.options.items && d.length && this.lazyPreload(b, d)) : b.data("owl-loaded", "loaded"))
            },
            lazyPreload: function(g, a) {
                var d, c = this,
                    e = 0;
                function f() {
                    g.data("owl-loaded", "loaded").removeClass("loading"), a.removeAttr("data-src"), "fade" === c.options.lazyEffect ? a.fadeIn(400) : a.show(), "function" == typeof c.options.afterLazyLoad && c.options.afterLazyLoad.apply(this, [c.$elem])
                }
                "DIV" === a.prop("tagName") ? (a.css("background-image", "url(" + a.data("src") + ")"), d = !0) : a[0].src = a.data("src"),
                    function g() {
                        e += 1, c.completeImg(a.get(0)) || !0 === d ? f() : e <= 100 ? b.setTimeout(g, 100) : f()
                    }()
            },
            autoHeight: function() {
                var d, c = this,
                    e = a(c.$owlItems[c.currentItem]).find("img");
                function f() {
                    var d = a(c.$owlItems[c.currentItem]).height();
                    c.wrapperOuter.css("height", d + "px"), c.wrapperOuter.hasClass("autoHeight") || b.setTimeout(function() {
                        c.wrapperOuter.addClass("autoHeight")
                    }, 0)
                }
                void 0 !== e.get(0) ? (d = 0, function a() {
                    d += 1, c.completeImg(e.get(0)) ? f() : d <= 100 ? b.setTimeout(a, 100) : c.wrapperOuter.css("height", "")
                }()) : f()
            },
            completeImg: function(a) {
                return !!a.complete && ("undefined" == typeof a.naturalWidth || 0 !== a.naturalWidth)
            },
            onVisibleItems: function() {
                var b;
                for (!0 === this.options.addClassActive && this.$owlItems.removeClass("active"), this.visibleItems = [], b = this.currentItem; b < this.currentItem + this.options.items; b += 1) this.visibleItems.push(b), !0 === this.options.addClassActive && a(this.$owlItems[b]).addClass("active");
                this.owl.visibleItems = this.visibleItems
            },
            transitionTypes: function(a) {
                this.outClass = "owl-" + a + "-out", this.inClass = "owl-" + a + "-in"
            },
            singleItemTransition: function() {
                var a = this,
                    g = a.outClass,
                    f = a.inClass,
                    c = a.$owlItems.eq(a.currentItem),
                    d = a.$owlItems.eq(a.prevItem),
                    h = Math.abs(a.positionsInArray[a.currentItem]) + a.positionsInArray[a.prevItem],
                    e = Math.abs(a.positionsInArray[a.currentItem]) + a.itemWidth / 2,
                    b = "webkitAnimationEnd oAnimationEnd MSAnimationEnd animationend";
                a.isTransition = !0, a.$owlWrapper.addClass("owl-origin").css({
                    "-webkit-transform-origin": e + "px",
                    "-moz-perspective-origin": e + "px",
                    "perspective-origin": e + "px"
                }), d.css(function(a) {
                    return {
                        position: "relative",
                        left: a + "px"
                    }
                }(h)).addClass(g).on(b, function() {
                    a.endPrev = !0, d.off(b), a.clearTransStyle(d, g)
                }), c.addClass(f).on(b, function() {
                    a.endCurrent = !0, c.off(b), a.clearTransStyle(c, f)
                })
            },
            clearTransStyle: function(a, b) {
                a.css({
                    position: "",
                    left: ""
                }).removeClass(b), this.endPrev && this.endCurrent && (this.$owlWrapper.removeClass("owl-origin"), this.endPrev = !1, this.endCurrent = !1, this.isTransition = !1)
            },
            owlStatus: function() {
                this.owl = {
                    userOptions: this.userOptions,
                    baseElement: this.$elem,
                    userItems: this.$userItems,
                    owlItems: this.$owlItems,
                    currentItem: this.currentItem,
                    prevItem: this.prevItem,
                    visibleItems: this.visibleItems,
                    isTouch: this.browser.isTouch,
                    browser: this.browser,
                    dragDirection: this.dragDirection
                }
            },
            clearEvents: function() {
                this.$elem.off(".owl owl mousedown.disableTextSelect"), a(c).off(".owl owl"), a(b).off("resize", this.resizer)
            },
            unWrap: function() {
                0 !== this.$elem.children().length && (this.$owlWrapper.unwrap(), this.$userItems.unwrap().unwrap(), this.owlControls && this.owlControls.remove()), this.clearEvents(), this.$elem.attr("style", this.$elem.data("owl-originalStyles") || "").attr("class", this.$elem.data("owl-originalClasses"))
            },
            destroy: function() {
                this.stop(), b.clearInterval(this.checkVisible), this.unWrap(), this.$elem.removeData()
            },
            reinit: function(b) {
                var c = a.extend({}, this.userOptions, b);
                this.unWrap(), this.init(c, this.$elem)
            },
            addItem: function(a, b) {
                var c;
                return !!a && (0 === this.$elem.children().length ? (this.$elem.append(a), this.setVars(), !1) : (this.unWrap(), (c = void 0 === b || -1 === b ? -1 : b) >= this.$userItems.length || -1 === c ? this.$userItems.eq(-1).after(a) : this.$userItems.eq(c).before(a), void this.setVars()))
            },
            removeItem: function(a) {
                var b;
                if (0 === this.$elem.children().length) return !1;
                b = void 0 === a || -1 === a ? -1 : a, this.unWrap(), this.$userItems.eq(b).remove(), this.setVars()
            }
        };
        a.fn.owlCarousel = function(b) {
            return this.each(function() {
                if (!0 === a(this).data("owl-init")) return !1;
                a(this).data("owl-init", !0);
                var c = Object.create(d);
                c.init(b, this), a.data(this, "owlCarousel", c)
            })
        }, a.fn.owlCarousel.options = {
            items: 5,
            itemsCustom: !1,
            itemsDesktop: [1199, 4],
            itemsDesktopSmall: [979, 3],
            itemsTablet: [768, 2],
            itemsTabletSmall: !1,
            itemsMobile: [479, 1],
            singleItem: !1,
            itemsScaleUp: !1,
            slideSpeed: 200,
            paginationSpeed: 800,
            rewindSpeed: 1e3,
            autoPlay: !1,
            stopOnHover: !1,
            navigation: !1,
            navigationText: ["prev", "next"],
            rewindNav: !0,
            scrollPerPage: !0,
            pagination: !1,
            paginationNumbers: !1,
            responsive: !0,
            responsiveRefreshRate: 200,
            responsiveBaseWidth: b,
            baseClass: "owl-carousel",
            theme: "owl-theme",
            lazyLoad: !1,
            lazyFollow: !0,
            lazyEffect: "fade",
            autoHeight: !1,
            jsonPath: !1,
            jsonSuccess: !1,
            dragBeforeAnimFinish: !0,
            mouseDrag: !0,
            touchDrag: !0,
            addClassActive: !1,
            transitionStyle: !1,
            beforeUpdate: !1,
            afterUpdate: !1,
            beforeInit: !1,
            afterInit: !1,
            beforeMove: !1,
            afterMove: !1,
            afterAction: !1,
            startDragging: !1,
            afterLazyLoad: !1
        }
    }(jQuery, window, document)