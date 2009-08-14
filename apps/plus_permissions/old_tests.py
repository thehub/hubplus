    def XtestSliders(self) :
        # PermissionSystem is the generic API to the permission system, 
        # it's where you can find most things you need.
        ps = PermissionSystem()

        # Locations currently mandatory for TgGroups, so let's have one
        l = Location(name='biosphere')
        l.save()

        # create a default group and admin
        group, adminGroup = create_site_group('greenarchitects','Green Architects', location=l,create_hosts=True)

        # create an example bit of content, a blog post of type "OurPost"
        blog = OurPost(title='test')
        blog.save()

        # create a user 
        u = User(username='phil',email_address='phil@the-hub.net')
        u.save()

        # another user (called 'author') who is set as the creator of our blog
        author = User(username='author',email_address='the-hub.net')
        author.display_name = 'author'
        author.save()

        # a group which is the top-level of our hierarchy of permission groups. everybody and anybody (even non-authenticated members of the public) 
        # are considered to be members of this group
        everyone = ps.get_anon_group()

        # all_members is all *members* of hubplus, anyone with an account
        all_members = ps.get_all_members_group()

        # the mermissions manager object for OurPosts
        pm = ps.get_permission_manager(OurPost)

        # the permission manager for OurPost knows how to make relevant sliders. 
        # we need to pass to it the resource itself, the name of the interface, 
        #     the agent which is the "owner" of the resource (in this case "group") and 
        #     the agent which is the "creator" of the resource (in this case "author")
        
        s = pm.get_interfaces()['Viewer'].make_slider_for(blog,pm.make_slider_options(blog,group,author),u,0,u)

        # now we're just testing that OurPost.Viewer has 5 options for the slider
        self.assertEquals(len(s.get_options()),5)

        # let's see them
        ops = s.get_options()
        self.assertEquals([a.name for a in ops],['World','All Members','Green Architects (owner)','author (creator)','Green Architecture Admin'])

        # and check that it gave us "World" (ie. the everyone group) as the view default. (we assume that blogs default to allowing non members to read them)
        self.assertEquals(s.get_current_option().name,'World')

        tif = ps.get_interface_factory()
        
        self.assertTrue(ps.has_access(everyone,blog,tif.get_id(OurPost,'Viewer')))
        self.assertFalse(ps.has_access(everyone,blog,tif.get_id(OurPost,'Editor')))
        self.assertTrue(ps.has_access(u,blog,tif.get_id(OurPost,'Viewer')))

        # now use the slider to *change* the permission. Behind the scenes this is manipulating SecurityTags.
        s.set_current_option(1) # is it ok to set option using numeric index? Or better with name?
        self.assertEquals(s.get_current_option().name,'All Members')
        self.assertFalse(ps.has_access(everyone,blog,tif.get_id(OurPost,'Viewer')))
        self.assertTrue(ps.has_access(all_members,blog,tif.get_id(OurPost,'Viewer')))

        # and again
        s.set_current_option(2) # group level
        self.assertEquals(s.get_current_option().name,'Green Architects (owner)')
        self.assertFalse(ps.has_access(all_members,blog,tif.get_id(OurPost,'Viewer')))
        self.assertTrue(ps.has_access(group,blog,tif.get_id(OurPost,'Viewer'))) 

        # and again
        s.set_current_option(3) # author
        self.assertEquals(s.get_current_option().name,'author (creator)')
        self.assertFalse(ps.has_access(group,blog,tif.get_id(OurPost,'Viewer')))
        self.assertTrue(ps.has_access(author,blog,tif.get_id(OurPost,'Viewer')))

        # and again
        s.set_current_option(4) # group level
        self.assertEquals(s.get_current_option().name,'Green Architecture Admin')
        self.assertFalse(ps.has_access(author,blog,tif.get_id(OurPost,'Viewer')))
        self.assertTrue(ps.has_access(adminGroup,blog,tif.get_id(OurPost,'Viewer')))


    def testSliderGroup(self) :
        u= User(username='paulo',email_address='paulo@the-hub.net')
        u.display_name=u.username
        u.save()
        
        p = u.get_profile()
        u = p.user
        
        ps = PermissionSystem()


        l = Location(name='biosphere2')
        l.save()

        group = TgGroup(group_name='organiccooks',display_name='Organic Cooks', place=l,created=datetime.date.today())
        group.save()
        #admin_group = TgGroup(group_name='ocadmin', display_name='Organic Cook Admin', place=l,created=datetime.date.today())
        #admin_group.save()
        #da = DefaultAdmin(agent=admin_group,resource=group)
        #da.save()
        blog = OurPost(title='slider testing')
        blog.save()


        pm = ps.get_permission_manager(OurPost)
        pm.setup_defaults(blog,group,u)

        # our permission manager, when it makes the sliders, needs to be able to report the default owner and admins etc.
        self.assertEquals(pm.get_owner(blog,ps.get_interface_id(OurPost,'Viewer')),group)
        self.assertEquals(pm.get_creator(blog,ps.get_interface_id(OurPost,'Viewer')),u)

        group_type = ContentType.objects.get_for_model(ps.get_anon_group()).id
        
        match = simplejson.dumps(
         {'sliders':{
          'title':'title',
          'intro':'intro',
          'resource_id':blog.id,
          'resource_type':ContentType.objects.get_for_model(blog).id, 
          'option_labels':['World','All Members','Organic Cooks (owner)','paulo (creator)' ],
          'option_types':[group_type,group_type,group_type,ContentType.objects.get_for_model(u).id],
          'option_ids':[ps.get_anon_group().id,ps.get_all_members_group().id,group.id,u.id],
          'sliders':['Viewer','Editor'],
          'interface_ids':[ps.get_interface_id(OurPost,'Viewer'),ps.get_interface_id(OurPost,'Editor')],
          'mins':[0,0],
          'constraints':[[0,1]],
          'current':[0,2],
          'extras':{}
          }}
        )

        json = pm.json_slider_group('title','intro',blog,['Viewer','Editor'],[0,0],[[0,1]])

        self.assertEquals(json,match)

    def Xtest_agent_constraint(self) :
        # there can only one agent from a collection of options
        # functions to find which option exists and to replace it with another from the set
        ps = get_permission_system()
        u=User(username='hermit',email_address='hermit@the-hub.net')
        u.save()
        b=OurPost(title='post')
        b.save()
        interface=ps.get_interface_id(OurPost,'Viewer')
        anon = ps.get_anon_group()
        all = ps.get_all_members_group()


        def kl(o) : return (ContentType.objects.get_for_model(o).id,o.id)
        
        kill_list = [kl(o) for o in [u, anon, all]]

        s=SecurityTag(name='blaaaah',agent=u,resource=b,interface=interface,creator=u)
        s.save()

        s2=SecurityTag(name='blaah',agent=anon,resource=b,interface=interface,creator=u)
        s2.save()

        u2=User(username='harry',email_address='harry@the-hub.net')
        u2.save()

        s2=SecurityTag(name='aae',agent=u2,resource=b,interface=interface,creator=u)
        s2.save()

        u_type = ContentType.objects.get_for_model(u)
        an_type = ContentType.objects.get_for_model(anon)
        r_type = ContentType.objects.get_for_model(b)

        # check there are three permissions for this
        for x in ps.get_permissions_for(b) : print x
        self.assertEquals(SecurityTag.objects.filter(resource_content_type=r_type,resource_object_id=b.id).count(),3)

        # and then when we kill them, there's only one left
        SecurityTag.objects.kill_list(kill_list,r_type,b.id,interface) 

        for x in ps.get_permissions_for(b) : print x
        self.assertEquals(SecurityTag.objects.filter(resource_content_type=r_type,resource_object_id=b.id).count(),1)

        u3 = User(username='jon',email_address='jon@the-hub.net')
        u3.save()

        s2=SecurityTag(name='bleaaaah',agent=u3,resource=b,interface=interface,creator=u)
        s2.save()
        self.assertTrue(ps.has_access(u3,b,interface))
   
        kill_list = [kl(o) for o in [u3, anon, all]]

        SecurityTag.objects.update(resource=b,interface=interface,new=all,kill=kill_list,name='boo',creator=u)

        self.assertFalse(ps.has_access(u3,b,interface))
        all.add_member(u3)
        self.assertTrue(ps.has_access(u3,b,interface))

        SecurityTag.objects.update(resource=b,interface=interface,new=u3,kill=kill_list,name='boo2',creator=u)
        self.assertTrue(ps.has_access(u3,b,interface))
        self.assertFalse(ps.has_access(all,b,interface))        


    def testUserWrapping(self) :
        u=User(username='oli',email_address='oli@the-hub.net')
        u.save()
        blog = OurPost(title='test wrapping')
        blog.save()

        blog = NullInterface(blog)

        ps = PermissionSystem()
        pm = ps.get_permission_manager(OurPost)

        #ipdb.set_trace()
        pm.setup_defaults(blog,u,u)
        perms = ps.get_permissions_for(blog)
        count = 0
        for x in perms :
            count=count+1
        self.assertEquals(count,3)

        # in this case, because of the defaults for blog u has access to all interfaces

        ps.get_all_members_group().add_member(u)

        blog.load_interfaces_for(u) 

        self.assertEquals(len(blog.get_interfaces()),3)

        u2=User(username='holly',email_address='holly@the-hub.net')
        u2.save()
        blog2=OurPost(title='test rapping')
        blog2.save()
        blog2=NullInterface(blog2)
        
        pm.setup_defaults(blog2,u2,u2)

        # in this case, u is only getting access to the Viewer & Commentor interfaces
        blog2.load_interfaces_for(u)

        self.assertEquals(len(blog2.get_interfaces()),2)
        

